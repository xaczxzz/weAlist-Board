from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import TaskStatus

class Task(BaseModel):
    __tablename__ = "tasks"

    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False,
        index=True
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    ticket_id = Column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    ticket = relationship("Ticket", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title})>"

    def mark_completed(self):
        from datetime import datetime, timezone
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(timezone.utc)
