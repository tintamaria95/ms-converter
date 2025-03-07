from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import asyncio

from run_mitmproxy import run_mitmdump


port = 8080
asyncio.run(run_mitmdump(port=8080, timeout=10))


app = FastAPI()

# Store updates to send to the frontend
updates = []
websocket_connections = set()


# WebSocket endpoint for frontend to connect
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.add(websocket)

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


# POST request endpoint to receive JSON data and send updates
@app.post("/api/submit")
async def submit_message(request: Request):
    body = await request.json()
    message_content = body.get("content")

    if message_content:
        updates.append(message_content)

        # Notify all connected WebSocket clients with the new update
        for ws in websocket_connections:
            try:
                await ws.send_text(message_content)
            except WebSocketDisconnect:
                websocket_connections.remove(ws)

        return {"message": "Received", "content": message_content}
    else:
        return {"error": "Content missing in the request"}, 400


# Serve the HTML page on root
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(content=file.read())
