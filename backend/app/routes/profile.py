from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User
from app.utils.common import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }

@router.patch("")
def update_profile(
    username: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if username:
        existing = db.query(User).filter(User.username == username, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        current_user.username = username
        db.commit()
        db.refresh(current_user)

    return {"message": "Profile updated", "username": current_user.username}
