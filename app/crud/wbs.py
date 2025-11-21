from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.wbs import WBS
from app.models.activity_wbs import ActivityWBS
from app.schemas.wbs import WBSCreate, WBSUpdate


def create_wbs(db: Session, wbs: WBSCreate) -> WBS:
    db_wbs = WBS(**wbs.dict())
    db.add(db_wbs)
    db.commit()
    db.refresh(db_wbs)
    return db_wbs


def get_wbs(db: Session, wbs_id: UUID) -> Optional[WBS]:
    return db.query(WBS).filter(WBS.wbs_id == wbs_id).first()


def get_all_wbs(db: Session, skip: int = 0, limit: int = 100) -> List[WBS]:
    return db.query(WBS).offset(skip).limit(limit).all()


def update_wbs(db: Session, wbs_id: UUID, wbs_update: WBSUpdate) -> Optional[WBS]:
    db_wbs = get_wbs(db, wbs_id)
    if db_wbs:
        update_data = wbs_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_wbs, field, value)
        db.commit()
        db.refresh(db_wbs)
    return db_wbs


def delete_wbs(db: Session, wbs_id: UUID) -> bool:
    db_wbs = get_wbs(db, wbs_id)
    if db_wbs:
        db.delete(db_wbs)
        db.commit()
        return True
    return False


def add_wbs_to_activity(db: Session, activity_id: UUID, wbs_id: UUID) -> ActivityWBS:
    db_activity_wbs = ActivityWBS(activity_id=activity_id, wbs_id=wbs_id)
    db.add(db_activity_wbs)
    db.commit()
    db.refresh(db_activity_wbs)
    return db_activity_wbs


def remove_wbs_from_activity(db: Session, activity_id: UUID, wbs_id: UUID) -> bool:
    db_activity_wbs = db.query(ActivityWBS).filter(
        ActivityWBS.activity_id == activity_id,
        ActivityWBS.wbs_id == wbs_id
    ).first()
    if db_activity_wbs:
        db.delete(db_activity_wbs)
        db.commit()
        return True
    return False


def get_wbs_for_activity(db: Session, activity_id: UUID) -> List[WBS]:
    return db.query(WBS).join(ActivityWBS).filter(
        ActivityWBS.activity_id == activity_id
    ).all()