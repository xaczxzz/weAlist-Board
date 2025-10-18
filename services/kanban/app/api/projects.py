from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.project import Project
from app.models.workspace import Workspace
from app.models.enums import ProjectStatus, Priority
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    """새로운 Project 생성"""
    # Workspace 존재 확인
    workspace = db.query(Workspace).filter(Workspace.id == project_in.workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {project_in.workspace_id} not found"
        )

    db_project = Project(**project_in.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    workspace_id: Optional[int] = Query(None),
    status_filter: Optional[ProjectStatus] = Query(None, alias="status"),
    priority: Optional[Priority] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Project 목록 조회 (필터링 및 페이지네이션)"""
    query = db.query(Project)

    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)
    if status_filter:
        query = query.filter(Project.status == status_filter)
    if priority:
        query = query.filter(Project.priority == priority)

    total = query.count()
    projects = query.order_by(Project.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "total": total,
        "items": projects,
        "limit": limit,
        "offset": offset
    }

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """특정 Project 조회"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Project 정보 수정"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Project 삭제 (Cascade로 하위 Ticket, Task 모두 삭제)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    db.delete(project)
    db.commit()
    return None
