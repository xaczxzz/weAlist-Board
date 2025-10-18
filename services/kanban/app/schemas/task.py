from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.enums import TaskStatus

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = TaskStatus.TODO

class TaskCreate(TaskBase):
    ticket_id: int = Field(..., gt=0)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskResponse(TaskBase):
    id: int
    ticket_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    total: int
    items: list[TaskResponse]
    limit: int
    offset: int

    class Config:
        from_attributes = True
