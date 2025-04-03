import re
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from assemble_pdf import create_pdf_from_images
from utils import get_score_parts, save_score_metadata, get_saved_scores_with_metadata
from config import config
from Score import ScorePage

from db.main import SessionLocal
from db.connection import get_session
from db.crud import get_score


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

websocket_connections: Set[WebSocket] = set()
mitmproxy_status = {"is_active": False}


def get_message_scores():
    """Returns JSON message to send list of scores available to download to frontend

    Returns:
        List: List of dict scores
    """
    scores_metadata = get_saved_scores_with_metadata(config["scores_directory"])
    return {"scores": scores_metadata}


def get_message_status():
    """Returns JSON message to update frontend status (active or inactive)

    Returns:
        Dict: dict status
    """
    return {"status": {"is_active": mitmproxy_status["is_active"]}}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    websocket_connections.add(ws)
    socket_message_scores = get_message_scores()
    socket_message_status = get_message_status()
    await ws.send_json(
        {
            k: v
            for d in [socket_message_scores, socket_message_status]
            for k, v in d.items()
        }
    )
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(ws)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.post("/api/score")
async def submit_score(request: Request):
    """
    POST request received on this route is supposed to come from MITMProxy script
    once it intercepted and downloaded a page of a score.
    """
    response = await request.json()
    score_page = ScorePage(
        id=response.get("id"),
        page=response.get("page"),
        title=response.get("title"),
        composer=response.get("composer"),
        author=response.get("author"),
    )
    save_score_metadata(score_page)
    for ws in websocket_connections:
        json_message = get_saved_scores_with_metadata(config["scores_directory"])
        await ws.send_json(json_message)
    return 200


@app.post("/api/status")
async def submit_status(request: Request):
    """
    POST request received on this route set status
    """
    response = await request.json()
    mitmproxy_status["is_active"] = response["is_active"]
    for ws in websocket_connections:
        await ws.send_json(get_message_status())
    return 200


@app.post("/api/download")
async def download_pdf(request: Request):
    """
    POST request received on this route is supposed to come from static frontend
    once the user confirms he wants to get PDF of pages for specific score id.
    """
    try:
        response = await request.json()
        score_id = response.get("score_id")
        db = get_session(maker=SessionLocal)
        score_name = get_score(db=db, score_id=score_id).title
        db.close()
        files_paths = get_score_parts(config["scores_directory"], score_id)
        sorted_filenames = sorted(
            files_paths, key=lambda x: int(re.match(r"(\d+)_", x).group(1))
        )
        sorted_file_paths = [
            f"{config['scores_directory']}/{score_id}/{f}" for f in sorted_filenames
        ]
        create_pdf_from_images(
            image_paths=sorted_file_paths,
            output_pdf_path=f"{config['output_directory']}/{score_name}.pdf",
        )
    except Exception as e:
        print(e)
