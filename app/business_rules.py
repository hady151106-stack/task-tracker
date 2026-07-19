"""Status-transition business rules for the Task Tracker API (Module 2, Part 2.3).

This VALID_TRANSITIONS set matches the instructor's video exactly:
the three forward/reopen transitions plus the three same-to-same pairs.
"""

from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
        (TaskStatus.TODO, TaskStatus.TODO),
        (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
        (TaskStatus.DONE, TaskStatus.DONE),
    }
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Raise HTTP 422 if (current, new) is not an allowed transition pair."""
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to {new.value}. "
                f"Allowed transitions: {allowed}"
            ),
        )
