import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Workspace, Project, Ticket, Task

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_workspace(db):
    workspace = Workspace(name="Test Workspace", description="For testing")
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
        priority=Priority.HIGH
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
        priority=Priority.MEDIUM
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
        status=TaskStatus.TODO
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
