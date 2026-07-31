# Task Tracker

A task board with a FastAPI backend and a vanilla JavaScript Kanban frontend, built across Modules 1-3 of the AI-Assisted Coding course and extended in the mid-course project.

## What it does

- Create, view, update, and delete tasks
- Three statuses: ToDo, InProgress, Done, with backend-enforced transition rules
- Priorities: Low, Medium, High, with cards sorted High to Low inside each column
- Drag-and-drop between columns, persisted through the API
- Create/edit modal with client-side title validation and server 422 handling
- **Due dates** with an overdue indicator and an overdue-only filter
- **Tags** with chips on cards and a tag filter that combines with the overdue filter

## Mid-course project features

**Due dates + overdue filter.** Tasks take an optional `due_date` (ISO `YYYY-MM-DD`). `TaskResponse` exposes a computed `is_overdue` field: true when the due date is strictly before the current UTC date and the status is not Done. `GET /tasks?overdue=true` returns only overdue tasks. The frontend shows the due date and a red Overdue pill on cards, plus an "Overdue only" checkbox.

**Tags / labels.** Tasks take an optional list of tags. Each tag is trimmed; blank tags return 422; duplicates are removed case-insensitively; more than five tags returns 422. The frontend renders tags as chips and provides a tag dropdown that combines with the overdue filter using AND.

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/health` | Returns 200 with a UTC timestamp |
| POST | `/tasks` | Creates a task, returns 201 |
| GET | `/tasks` | Lists tasks; optional `status`, `priority`, and `overdue` query filters |
| GET | `/tasks/{task_id}` | Returns one task, or 404 |
| PATCH | `/tasks/{task_id}` | Partial update; invalid status transitions return 422 |
| DELETE | `/tasks/{task_id}` | Returns 204, or 404 |

Swagger docs at `http://localhost:8000/docs`.

## Project structure

```
task-tracker/
+-- app/
|   +-- main.py            # FastAPI app, CORS, and all routes
|   +-- models.py          # Pydantic v2 models, enums, validators
|   +-- storage.py         # In-memory storage with helper functions
|   +-- business_rules.py  # VALID_TRANSITIONS and validate_status_transition
+-- frontend/
|   +-- index.html         # Single-file vanilla HTML/CSS/JS Kanban board
+-- tests/
|   +-- conftest.py        # TestClient and autouse storage reset fixtures
|   +-- test_tasks.py      # 29 pytest tests
|   +-- verify_a.py        # Module 2 model verification script
+-- docs/midcourse/        # Mid-course project documentation
+-- BEHAVIOR_CONTRACT.md   # C1-C14 manual behaviour checklist
+-- DEBUGGING_LOG.md
+-- requirements.txt
+-- README.md
```

Storage is in-memory only, so tasks are lost when the backend restarts. There is no database and no authentication.

## How to run

**1. Backend.** From the project root, activate the virtual environment and start the server:

```
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000` and Swagger docs at `http://localhost:8000/docs`.

**2. Frontend.** In a second terminal from the project root:

```
python -m http.server 5500
```

Open `http://localhost:5500/frontend/index.html`. The backend must be running first, or the board shows its error state.

**3. Tests.** With the virtual environment active, from the project root:

```
pytest -q
```

Expected result: **29 passed**.

## Setup from scratch

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Linux or macOS, use `source venv/bin/activate` instead.

## Documentation

`docs/midcourse/` contains the user stories, mini-ADR, prompt log, verification evidence, and reflection for the mid-course project.

## Final Project

Branch reviewed: final-project

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API runs at http://localhost:8000 and Swagger docs at http://localhost:8000/docs. For the frontend, in a second terminal from the project root: `python -m http.server 5500`, then open http://localhost:5500/frontend/index.html.

### How to run tests

```
venv\Scripts\activate
pytest -q
```

Expected result: 29 passed.

### How to run with Docker

```
docker build -t task-tracker:dev .
docker run -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
```

The /health endpoint returns HTTP 200. The container runs as a non-root user (app).

### Evidence files

- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary

AI helped draft or review: CI, Docker, docs, and security review. I verified the work by: running pytest (29 passed), reviewing each diff, building and running the Docker container, checking /health returned 200, and grading every AI review comment and security finding myself. One AI suggestion I rejected or corrected: I rejected adding --reload to the Docker container CMD, because it is a development-only feature that does not belong in a runtime image.
