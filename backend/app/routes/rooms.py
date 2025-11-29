import base64
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import ChatRoom, UserRoom
from app.utils.common import get_current_user

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("")
def list_rooms(search: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(ChatRoom)
    if search:
        query = query.filter(ChatRoom.name.ilike(f"%{search}%"))
    rooms = query.all()
    return [{"id": r.id, "name": r.name} for r in rooms]

@router.post("")
def create_room(
    name: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = db.query(ChatRoom).filter_by(name=name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")

    key = base64.b64encode(os.urandom(32)).decode()
    room = ChatRoom(name=name, symmetric_key=key)
    db.add(room)
    db.commit()
    db.refresh(room)

    link = UserRoom(user_id=current_user.id, room_id=room.id)
    db.add(link)
    db.commit()
    return {"id": room.id, "name": room.name}

@router.post("/{room_id}/join")
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = db.query(ChatRoom).get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    existing = db.query(UserRoom).filter_by(user_id=current_user.id, room_id=room_id).first()
    if existing:
        return {"message": "Already joined"}

    link = UserRoom(user_id=current_user.id, room_id=room_id)
    db.add(link)
    db.commit()
    return {"message": f"Joined room '{room.name}'"}
