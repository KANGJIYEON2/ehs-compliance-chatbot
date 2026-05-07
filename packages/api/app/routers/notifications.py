"""알림 라우터"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def create_notification(db: Session, user_id: str, type: str, title: str, message: str, link: str | None = None):
    """알림 생성 헬퍼 (다른 라우터에서 호출)"""
    n = Notification(user_id=user_id, type=type, title=title, message=message, link=link)
    db.add(n)


@router.get("")
def list_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    items = query.order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()

    return {
        "unread_count": unread_count,
        "items": [
            {
                "id": n.id, "type": n.type, "title": n.title,
                "message": n.message, "link": n.link,
                "is_read": n.is_read, "created_at": n.created_at.isoformat(),
            }
            for n in items
        ],
    }


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"status": "ok"}


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"status": "ok"}
