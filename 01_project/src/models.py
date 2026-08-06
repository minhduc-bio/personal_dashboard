from typing import Optional, Literal, List
from pydantic import BaseModel

class Task(BaseModel):
    """Schema định nghĩa cấu trúc cho một công việc (Task)."""
    id: str
    title: str
    mood_affinity: Literal["High", "Neutral", "Low"]
    status: Literal["pending", "done"]
    created_at: str

class Session(BaseModel):
    """Schema định nghĩa cấu trúc cho một phiên làm việc trong ngày (Session)."""
    date: str
    state: Literal["Created", "Planning", "Active", "Reviewing", "Closed"]
    mood: Optional[str] = None
    task_ids: List[str] = []