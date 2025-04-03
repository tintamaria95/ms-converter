from sqlalchemy.orm import Session
from db.models import ScoreMetadataModel
from Score import ScorePage


def get_score(db: Session, score_id: str):
    return (
        db.query(ScoreMetadataModel).filter(ScoreMetadataModel.id == score_id).first()
    )


def get_all_scores(db: Session):
    return db.query(ScoreMetadataModel).all()


def create_score(db: Session, score: ScorePage):
    score = ScoreMetadataModel(
        id=score.id, title=score.title, author=score.author, composer=score.composer
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def delete_score(db: Session, score_id: str):
    obj = db.query(ScoreMetadataModel).filter_by(id=score_id).first()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False
