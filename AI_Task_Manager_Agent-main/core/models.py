from pydantic import BaseModel
from typing import List, Optional, Literal


class CategorizedTask(BaseModel):
    category: Literal["Development", "Research", "Admin", "Urgent"]
    priority: Literal["High", "Medium", "Low"]
    summary: str
    tags: List[str] = []
    estimated_duration: Optional[str] = None


class Task(BaseModel):
    task_id: str
    original_input: str
    category: str
    priority: str
    summary: str
    tags: List[str] = []
    estimated_duration: Optional[str] = None
    status: Literal["Pending", "In Progress", "Complete", "Blocked"] = "Pending"
    timestamp: str
