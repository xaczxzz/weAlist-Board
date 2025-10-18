from sqlalchemy import Column, String, Text, Integer, Enum as SQLEnum
from app.models.base import BaseModel
from app.models.enums import TicketStatus, Priority

class Ticket(BaseModel):
    __tablename__ = "tickets"

    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )
    priority = Column(
        SQLEnum(Priority),
        default=Priority.MEDIUM,
        nullable=False,
        index=True
    )

    # FK 제거: 샤딩 및 DB 분리 대비
    project_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="References projects.id (no FK for sharding)"
    )

    def __repr__(self):
        return f"<Ticket(id={self.id}, title={self.title})>"
