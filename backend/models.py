from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationships
    # Cascade delete: When user is deleted, delete their files and messages
    files = relationship("ConversationFile", back_populates="owner", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="owner", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="owner", cascade="all, delete-orphan")
    thoughts = relationship("Thought", back_populates="owner", cascade="all, delete-orphan")

class ConversationFile(Base):
    __tablename__ = "conversation_files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, index=True)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="files")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    audio_path = Column(String, nullable=True) # Path to generated audio for this message (if any)
    vector = Column(LargeBinary, nullable=True) # Semantic embedding
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="messages")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String) # 'static' or 'dynamic'
    content = Column(Text)
    vector = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="preferences")

class Thought(Base):
    __tablename__ = "thoughts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    content = Column(Text)
    mood = Column(String)
    vector = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="thoughts")
