from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
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

    project_id = Column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    project = relationship("Project", back_populates="tickets")
    tasks = relationship(
        "Task",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ticket(id={self.id}, title={self.title})>"
