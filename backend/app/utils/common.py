import os, base64
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.models.models import User, ChatRoom, RoomUserSetting
from app.database.database import get_db
from dotenv import load_dotenv

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        uid = payload.get("uid")
        if not sub and not uid:
            return None
    except JWTError as e:
        print("JWT decode error:", e)
        return None

    user = None
    if uid and str(uid).isdigit():
        user = db.query(User).filter(User.id == int(uid)).first()
    elif sub:
        user = db.query(User).filter(User.username == sub).first()
    return user

async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")

    token = parts[1]
    user = get_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")
    return user

def get_or_create_chatroom(db: Session, chat_id: str) -> ChatRoom:
    room = db.query(ChatRoom).filter_by(name=chat_id).first()
    if not room:
        key = base64.b64encode(os.urandom(32)).decode()
        room = ChatRoom(name=chat_id, symmetric_key=key)
        db.add(room)
        db.commit()
        db.refresh(room)
        print(f"Created new chatroom: {chat_id}")
    elif not room.symmetric_key:
        room.symmetric_key = base64.b64encode(os.urandom(32)).decode()
        db.commit()
    return room

def get_or_create_room_user_setting(db: Session, user_id: int, room_id: int) -> RoomUserSetting:
    setting = db.query(RoomUserSetting).filter_by(user_id=user_id, room_id=room_id).first()
    if not setting:
        setting = RoomUserSetting(user_id=user_id, room_id=room_id, filter_enabled=False)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting
