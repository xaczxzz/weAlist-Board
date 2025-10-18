from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class WorkspaceResponse(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

class WorkspaceListResponse(BaseModel):
    total: int
    items: list[WorkspaceResponse]
    limit: int
    offset: int

    class Config:
        from_attributes = True
