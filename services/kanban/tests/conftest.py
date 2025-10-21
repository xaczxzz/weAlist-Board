import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Workspace, Project, Ticket, Task
from app.auth import get_current_user_id

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테스트용 user_id
TEST_USER_ID = 1

def override_get_current_user_id():
    """테스트 환경에서 JWT 인증을 우회하고 고정된 user_id 반환"""
    return TEST_USER_ID

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # startup/shutdown event handlers 제거 (테스트 환경)
    app.router.on_startup = []
    app.router.on_shutdown = []

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_workspace(db):
    workspace = Workspace(
        name="Test Workspace",
        description="For testing",
        created_by=TEST_USER_ID
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace

@pytest.fixture(scope="function")
def sample_project(db, sample_workspace):
    from app.models.enums import ProjectStatus, Priority
    project = Project(
        name="Test Project",
        workspace_id=sample_workspace.id,
        status=ProjectStatus.ACTIVE,
        priority=Priority.HIGH,
        created_by=TEST_USER_ID
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@pytest.fixture(scope="function")
def sample_ticket(db, sample_project):
    from app.models.enums import TicketStatus, Priority
    ticket = Ticket(
        title="Test Ticket",
        project_id=sample_project.id,
        status=TicketStatus.OPEN,
        priority=Priority.MEDIUM,
        created_by=TEST_USER_ID
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@pytest.fixture(scope="function")
def sample_task(db, sample_ticket):
    from app.models.enums import TaskStatus
    task = Task(
        title="Test Task",
        ticket_id=sample_ticket.id,
        status=TaskStatus.TODO,
        created_by=TEST_USER_ID
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
