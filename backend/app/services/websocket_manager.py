import json
from typing import Dict, List, Any, Optional
from fastapi import WebSocket
from app.models.models import Message

class ConnectionManager:

    def __init__(self):
        self.active: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(
        self, room_name: str, ws: WebSocket, user_id: int, username: str, filter_enabled: bool
    ):
        self.active.setdefault(room_name, []).append(
            {"ws": ws, "user_id": user_id, "username": username, "filter_enabled": filter_enabled}
        )

    def disconnect(self, room_name: str, ws: WebSocket):
        conns = self.active.get(room_name, [])
        self.active[room_name] = [c for c in conns if c["ws"] != ws]
        if not self.active[room_name]:
            del self.active[room_name]

    async def broadcast_message(
        self, room_name: str, message_obj: Message, plaintext: Optional[str] = None
    ):

        conns = self.active.get(room_name, [])
        out_common = {
            "type": "message",
            "id": message_obj.id,
            "from_user_id": message_obj.sender_id,
            "timestamp": message_obj.timestamp.isoformat(),
            "is_toxic": bool(message_obj.is_toxic),
            "prob": float(message_obj.toxicity_prob),
        }

        for conn in conns:
            try:
                if message_obj.is_toxic and conn["filter_enabled"]:
                    await conn["ws"].send_text(
                        json.dumps(
                            {
                                "type": "message_hidden",
                                "id": message_obj.id,
                                "note": "Message hidden due to your filter setting.",
                            }
                        )
                    )
                else:
                    await conn["ws"].send_text(
                        json.dumps(
                            {
                                **out_common,
                                "from_username": conn["username"],
                                "from_user_id": message_obj.sender_id,
                                "ciphertext": message_obj.ciphertext,
                            }
                        )
                    )

            except Exception:
                pass

    async def broadcast_presence(self, room_name: str, username: str, status: str):
        conns = self.active.get(room_name, [])
        for conn in conns:
            try:
                await conn["ws"].send_text(
                    json.dumps({"event": "presence", "user": username, "status": status})
                )
            except Exception:
                pass

manager = ConnectionManager()
