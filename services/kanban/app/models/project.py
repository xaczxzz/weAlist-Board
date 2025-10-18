from sqlalchemy import Column, String, Text, Integer, Enum as SQLEnum
from app.models.base import BaseModel
from app.models.enums import ProjectStatus, Priority

class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PLANNING,
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
    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="References workspaces.id (no FK for sharding)"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"
