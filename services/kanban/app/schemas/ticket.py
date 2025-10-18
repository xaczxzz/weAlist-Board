from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.enums import TicketStatus, Priority

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=2000)
    status: TicketStatus = TicketStatus.OPEN
    priority: Priority = Priority.MEDIUM

class TicketCreate(TicketBase):
    project_id: int = Field(..., gt=0)
    assignee_id: Optional[int] = Field(None, gt=0, description="담당자 ID")

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[Priority] = None
    assignee_id: Optional[int] = Field(None, gt=0, description="담당자 ID")

class TicketResponse(TicketBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    assignee_id: Optional[int] = None

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    total: int
    items: list[TicketResponse]
    limit: int
    offset: int

    class Config:
        from_attributes = True
