"""Task Tracker - FastAPI application (Module 2).

Module 1 gave this app a /health endpoint. Module 2 adds five CRUD endpoints
wired to the in-memory storage layer, plus status-transition business rules
enforced on PATCH.
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import (
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

app = FastAPI(
    title="Task Tracker API",
    description="Module 2 backend: CRUD endpoints, storage, and transition rules.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/health")
def health_check():
    """Return service health with the current UTC timestamp in ISO format."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str):
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return None
