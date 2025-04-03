from pathlib import Path

from Score import ScorePage
from db.main import SessionLocal
from db.connection import get_session
from db.crud import get_score, create_score


def get_score_parts(directory: str, score_id: str):
    score_dir = Path(directory) / score_id
    return [f.name for f in score_dir.iterdir() if f.is_file()]


def get_scores_ids(directory: str):
    return [d.name for d in Path(directory).iterdir() if d.is_dir()]


def save_score_metadata(score_page: ScorePage):
    try:
        db = get_session(maker=SessionLocal)
        if get_score(db=db, score_id=score_page.id) is None:
            create_score(db=db, score=score_page)
    finally:
        db.close()


def get_saved_scores_with_metadata(directory: str):
    saved_scores = []
    score_ids = get_scores_ids(directory)
    try:
        db = get_session(maker=SessionLocal)
        for score_id in score_ids:
            num_pages = len(get_score_parts(directory, score_id))
            score = get_score(db=db, score_id=score_id)
            if score:
                metadata = {
                    "id": score_id,
                    "num_pages": num_pages,
                    "title": score.title,
                    "author": score.author,
                    "composer": score.composer,
                }
                saved_scores.append(metadata)
    finally:
        db.close()
    return saved_scores
