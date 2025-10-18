from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.ticket import Ticket
from app.models.project import Project
from app.models.enums import TicketStatus, Priority
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse
)

router = APIRouter()

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    """새로운 Ticket 생성"""
    # Project 존재 확인
    project = db.query(Project).filter(Project.id == ticket_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {ticket_in.project_id} not found"
        )

    db_ticket = Ticket(**ticket_in.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/", response_model=TicketListResponse)
async def list_tickets(
    project_id: Optional[int] = Query(None),
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    priority: Optional[Priority] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Ticket 목록 조회 (필터링 및 페이지네이션)"""
    query = db.query(Ticket)

    if project_id:
        query = query.filter(Ticket.project_id == project_id)
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if priority:
        query = query.filter(Ticket.priority == priority)

    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).limit(limit).offset(offset).all()

    return {
        "total": total,
        "items": tickets,
        "limit": limit,
        "offset": offset
    }

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """특정 Ticket 조회"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db)
):
    """Ticket 정보 수정"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )

    update_data = ticket_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Ticket 삭제 (Cascade로 하위 Task 모두 삭제)"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )

    db.delete(ticket)
    db.commit()
    return None
