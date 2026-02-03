from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr 
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        from_attributes = True

class ConversationFileBase(BaseModel):
    filename: str

class ConversationFileCreate(ConversationFileBase):
    content: str

class ConversationFile(ConversationFileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    role: str
    content: str
    audio_path: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True