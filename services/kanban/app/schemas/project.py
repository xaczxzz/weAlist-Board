from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.enums import ProjectStatus, Priority

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: ProjectStatus = ProjectStatus.PLANNING
    priority: Priority = Priority.MEDIUM

class ProjectCreate(ProjectBase):
    workspace_id: int = Field(..., gt=0)

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None

class ProjectResponse(ProjectBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    total: int
    items: list[ProjectResponse]
    limit: int
    offset: int

    class Config:
        from_attributes = True
