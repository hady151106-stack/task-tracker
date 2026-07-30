# AGENTS.md - Task Tracker

Repo-level instructions for AI coding agents (Codex App, Claude Code, or chat-based
assistants) working in this repository. Read this file first.

## Project summary

Task Tracker is a small Kanban task board. It has a FastAPI backend with in-memory
storage and a single-file vanilla JavaScript frontend. It was built across Modules 1-3
of the AI-Assisted Coding course and extended in the mid-course project with due dates,
an overdue filter, and tags. There is no database and no authentication; tasks are lost
when the backend restarts.

## Tech stack

- Python 3.11
- FastAPI (backend framework)
- Pydantic v2 (validation models)
- Uvicorn (ASGI server)
- pytest + httpx (tests)
- Vanilla HTML/CSS/JavaScript (frontend, single file)

## Run and test commands (Windows / CMD)

Setup (once):

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

Run the backend:

    venv\Scripts\activate
    uvicorn app.main:app --reload --port 8000

API runs at http://localhost:8000, Swagger docs at http://localhost:8000/docs.

Run the frontend (second terminal, from the project root):

    python -m http.server 5500

Then open http://localhost:5500/frontend/index.html. The backend must be running first.

Run the tests:

    venv\Scripts\activate
    pytest -q

Expected result: 29 passed.

## Business rules (as implemented in code)

Statuses (app/models.py, TaskStatus): ToDo, InProgress, Done.

Priorities (app/models.py, TaskPriority): Low, Medium, High.

Title (app/models.py, _validate_title): required; trimmed of whitespace; blank
titles are rejected; titles longer than 200 characters are rejected.

Tags (app/models.py, _validate_tags): optional list; each tag is trimmed; blank tags
are rejected; duplicates are removed case-insensitively; more than 5 tags is rejected.

Due date and overdue (app/models.py, TaskResponse.is_overdue): a computed field that is
true when the due date is strictly before the current UTC date AND the status is not Done.

Status transitions (app/business_rules.py, VALID_TRANSITIONS): the following pairs
return 200; every other pair returns HTTP 422:

    ToDo -> InProgress
    InProgress -> Done
    Done -> InProgress        (reopen)
    ToDo -> ToDo              (same-status, no-op allowed)
    InProgress -> InProgress  (same-status, no-op allowed)
    Done -> Done              (same-status, no-op allowed)

Input models use extra="forbid" (app/models.py): unknown fields are rejected with 422.
Server-managed fields (id, created_at, updated_at) are generated in app/storage.py and
never accepted from client input.

Endpoints (app/main.py):

    GET    /health          -> 200 with a UTC timestamp
    POST   /tasks           -> 201
    GET    /tasks           -> 200 (optional status, priority, overdue filters)
    GET    /tasks/{id}      -> 200, or 404 if not found
    PATCH  /tasks/{id}      -> 200, or 422 on invalid transition, or 404 if not found
    DELETE /tasks/{id}      -> 204, or 404 if not found

CORS (app/main.py): allowed origins are http://localhost:5500, http://127.0.0.1:5500,
http://localhost:5173, and null; credentials disabled.

## Guardrails for AI agents

- Docs-first: new work for the final project lives in docs/. Do not create product features.
- Read-only by default: inspect and propose before changing anything.
- One task per thread: keep each session focused on a single bounded task.
- Do not change app/ or frontend/ except for a small bug fix, security fix, or
  documentation-supported correction, and only with explicit approval. Any such change
  must be explained in docs/final-ai-review.md.
- No new product features: do not add comments, authentication, a production database,
  notifications, or unrelated UI changes.

## Security and governance reminders

- Never paste or commit secrets: no credentials, tokens, .env values, production logs,
  or real personal/customer data in AI tools or in the repo. (.env is gitignored;
  .env.example contains only non-secret placeholder keys.)
- Do not run destructive commands (for example, deleting files or force-pushing) without
  explicit approval.
- Cite actual files when making claims about this repo. If something is not visible in
  the code, say "not confirmed" instead of inventing it.
- Do not invent findings, tests, or behavior that the code does not show.