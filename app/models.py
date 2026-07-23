"""Pydantic v2 data models for the Task Tracker API (Module 2, Part 2.1).

Defines the status/priority enums and the request/response models. Client input
models (TaskCreate, TaskUpdate) forbid extra fields and never accept
server-managed fields (id, created_at, updated_at).
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _validate_title(value: str) -> str:
    """Strip whitespace, reject blank titles, reject titles over 200 chars."""
    stripped = value.strip()
    if not stripped:
        raise ValueError("Title is required and cannot be blank")
    if len(stripped) > 200:
        raise ValueError("Title cannot be longer than 200 characters")
    return stripped


def _validate_tags(value: list[str]) -> list[str]:
    """Normalize tags by stripping whitespace, rejecting blanks, and deduplicating."""
    normalized: list[str] = []
    seen: set[str] = set()

    for tag in value:
        stripped = tag.strip()
        if not stripped:
            raise ValueError("Tags cannot be blank")

        key = stripped.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(stripped)

    if len(normalized) > 5:
        raise ValueError("A task cannot have more than 5 tags")

    return normalized


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str) -> str:
        return _validate_title(value)

    @field_validator("tags")
    @classmethod
    def check_tags(cls, value: list[str]) -> list[str]:
        return _validate_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def check_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_title(value)

    @field_validator("tags")
    @classmethod
    def check_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        return _validate_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return (
            self.due_date is not None
            and self.due_date < datetime.now(timezone.utc).date()
            and self.status is not TaskStatus.DONE
        )
