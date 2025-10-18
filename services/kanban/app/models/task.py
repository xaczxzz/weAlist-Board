from sqlalchemy import Column, String, Text, Integer, Enum as SQLEnum, DateTime
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

    # FK 제거: 샤딩 및 DB 분리 대비
    ticket_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="References tickets.id (no FK for sharding)"
    )

    # 담당자 (Member 서비스 users 테이블 참조)
    assignee_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="References users.id from Member service - 작업 담당자"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title})>"

    def mark_completed(self):
        from datetime import datetime, timezone
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(timezone.utc)
