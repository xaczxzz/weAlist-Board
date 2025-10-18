from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class AuditMixin:
    """사용자 감사(Audit) 정보 - Member 팀의 users 테이블 참조"""
    created_by = Column(
        Integer,
        nullable=False,
        index=True,
        comment="References users.id from Member service (no FK for microservice)"
    )
    updated_by = Column(
        Integer,
        nullable=True,
        index=True,
        comment="References users.id from Member service (no FK for microservice)"
    )

class BaseModel(Base, TimestampMixin, AuditMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
