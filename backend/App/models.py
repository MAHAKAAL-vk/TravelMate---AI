# models.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    user_query: str

class ChatResponse(BaseModel):
    summary: Optional[str] = ""
    table: Optional[str] = ""
