from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

from app.models import (
    Workspace,
    Project,
    Ticket,
    Task
)

from app.api import workspaces, projects, tickets, tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    if settings.ENV == "development":
        Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "env": settings.ENV,
        "version": settings.VERSION
    }

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs" if settings.DEBUG else "disabled"
    }

app.include_router(workspaces.router, prefix="/api/workspaces", tags=["workspaces"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
