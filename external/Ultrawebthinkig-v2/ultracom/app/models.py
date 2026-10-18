from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Role = Literal["client","technician","admin"]

class MessageIn(BaseModel):
    room: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1, max_length=8000)

class MessageOut(BaseModel):
    id: int
    room: str
    role: Role
    sender: str
    text: str
    ts: datetime

class SendDTO(BaseModel):
    room: str
    role: Role
    sender: str
    text: str

class HistoryQuery(BaseModel):
    room: str
    limit: int = 50
    offset: int = 0
