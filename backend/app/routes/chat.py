import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Header, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db, SessionLocal
from app.models.models import Message, User, ChatRoom
from app.services.encryption import decrypt_message
from app.services.toxicity import predict_toxicity, clean_text
from app.services.websocket_manager import manager
from app.utils.common import get_user_from_token, get_or_create_chatroom, get_or_create_room_user_setting

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/{chat_id}/key")
def get_chat_key(chat_id: str, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    room = get_or_create_chatroom(db, chat_id)
    user_pref = None

    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            user = get_user_from_token(token, db)
            if user:
                setting = db.query(ChatRoom.room_settings.property.mapper.class_).filter_by(
                    user_id=user.id, room_id=room.id
                ).first()
                user_pref = bool(setting.filter_enabled) if setting else False

    return {
        "chat_id": chat_id,
        "symmetric_key": room.symmetric_key,
        "user_filter": user_pref,
    }

@router.post("/{chat_id}/filter")
def set_room_filter(chat_id: str, enabled: bool, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = parts[1]
    user = get_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    room = db.query(ChatRoom).filter_by(name=chat_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    setting = get_or_create_room_user_setting(db, user.id, room.id)
    setting.filter_enabled = bool(enabled)
    db.commit()

    return {"chat_id": chat_id, "filter_enabled": setting.filter_enabled}

@router.get("/{chat_id}/history")
def get_chat_history(chat_id: str, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):

    room = db.query(ChatRoom).filter_by(name=chat_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    filter_enabled = False
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            user = get_user_from_token(token, db)
            if user:
                setting = db.query(ChatRoom.room_settings.property.mapper.class_).filter_by(
                    user_id=user.id, room_id=room.id
                ).first()
                filter_enabled = bool(setting.filter_enabled) if setting else False

    query = db.query(Message).filter_by(room_id=room.id).order_by(Message.timestamp.asc())
    if filter_enabled:
        query = query.filter(Message.is_toxic == False)

    messages = query.all()
    history = []

    for msg in messages:
        try:
            plaintext = decrypt_message(room.symmetric_key, msg.ciphertext)
        except Exception:
            plaintext = "[decryption_error]"

        sender = db.query(User).get(msg.sender_id)

        history.append({
            "id": msg.id,
            "from": sender.username if sender else "unknown",
            "sender_id": msg.sender_id,       
            "text": plaintext,
            "ciphertext": msg.ciphertext,    
            "toxic": bool(msg.is_toxic),
            "prob": float(msg.toxicity_prob),
            "timestamp": msg.timestamp.isoformat(),
        })

    return {
        "chat_id": chat_id,
        "messages": history,
        "filter_enabled": filter_enabled,
    }

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    user = get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008)
        db.close()
        return

    username = user.username
    room = get_or_create_chatroom(db, chat_id)
    key = room.symmetric_key

    setting = db.query(ChatRoom.room_settings.property.mapper.class_).filter_by(
        user_id=user.id, room_id=room.id
    ).first()
    filter_enabled = bool(setting.filter_enabled) if setting else False

    await websocket.accept()
    await manager.connect(chat_id, websocket, user.id, username, filter_enabled)
    await manager.broadcast_presence(chat_id, username, "online")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload.get("event") == "typing":
                conns = manager.active.get(chat_id, [])
                for c in conns:
                    if c["ws"] != websocket:
                        try:
                            await c["ws"].send_text(
                                json.dumps({
                                    "event": "typing",
                                    "from": username,
                                    "is_typing": payload.get("is_typing", False),
                                })
                            )
                        except Exception:
                            pass
                continue

            cipher = payload.get("ciphertext")
            if not cipher:
                continue

            try:
                plaintext = decrypt_message(key, cipher)
            except Exception:
                plaintext = None

            cleaned = clean_text(plaintext or "")
            pred, prob = predict_toxicity(cleaned)
            is_toxic = bool(pred) and (prob and prob > 0.0)

            msg = Message(
                room_id=room.id,
                sender_id=user.id,
                ciphertext=cipher,
                is_toxic=is_toxic,
                toxicity_prob=prob or 0.0,
                timestamp=datetime.utcnow(),
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)

            await manager.broadcast_message(chat_id, msg, plaintext or "")

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
        await manager.broadcast_presence(chat_id, username, "offline")
    finally:
        db.close()
