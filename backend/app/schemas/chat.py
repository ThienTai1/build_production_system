from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    latency: str
    sources: List[str]
