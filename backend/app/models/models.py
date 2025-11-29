from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    user_rooms = relationship("UserRoom", back_populates="user", cascade="all, delete-orphan")
    room_settings = relationship("RoomUserSetting", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username!r})>"

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    symmetric_key = Column(String(256), nullable=True) 

    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    members = relationship("UserRoom", back_populates="room", cascade="all, delete-orphan")
    room_settings = relationship("RoomUserSetting", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatRoom(name={self.name!r})>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    ciphertext = Column(Text, nullable=False) 
    is_toxic = Column(Boolean, default=False)
    toxicity_prob = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", back_populates="messages")
    room = relationship("ChatRoom", back_populates="messages")

    def __repr__(self):
        return f"<Message(sender_id={self.sender_id}, room_id={self.room_id}, toxic={self.is_toxic})>"

class UserRoom(Base):
    __tablename__ = "user_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_rooms")
    room = relationship("ChatRoom", back_populates="members")

    __table_args__ = (UniqueConstraint("user_id", "room_id", name="unique_user_room"),)

    def __repr__(self):
        return f"<UserRoom(user_id={self.user_id}, room_id={self.room_id})>"

class RoomUserSetting(Base):
    __tablename__ = "room_user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    filter_enabled = Column(Boolean, default=False)

    user = relationship("User", back_populates="room_settings")
    room = relationship("ChatRoom", back_populates="room_settings")

    __table_args__ = (UniqueConstraint("user_id", "room_id", name="unique_user_setting"),)

    def __repr__(self):
        return (
            f"<RoomUserSetting(user_id={self.user_id}, "
            f"room_id={self.room_id}, filter_enabled={self.filter_enabled})>"
        )
