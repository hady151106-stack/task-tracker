# Task Tracker API — Module 1 Skeleton

A minimal FastAPI skeleton for the AI-Assisted Coding course Task Tracker project.

This is the **Module 1 foundation only**. It runs a FastAPI application with a
single `GET /health` endpoint and Swagger documentation. CRUD task endpoints,
validation models, and storage are added in later modules.

## Scope

**Included in Module 1**
- FastAPI application (`app/main.py`)
- `GET /health` endpoint returning HTTP 200 and JSON
- Project folder structure ready for the backend
- Swagger docs at `/docs`

**Explicitly excluded in Module 1**
- Create/view/update/delete task endpoints
- Authentication and user accounts
- Database / persistence implementation
- Docker, cloud deployment, frontend, notifications, real-time updates

## Architecture

Module 1 architecture decision: **FastAPI + JSON file storage (Option A)** —
the simplest approach appropriate for a first learning project. No storage code
is written yet; the `app/storage/` folder is reserved for Module 2.

## Project structure

```
task-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app + /health endpoint
│   ├── api/
│   │   └── routes/        # route modules (Module 2)
│   ├── core/              # config / settings
│   ├── models/            # Pydantic models (Module 2)
│   └── storage/           # JSON file storage (Module 2)
├── tests/                 # pytest tests
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment, then install dependencies.

**Linux / macOS (bash)**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

After installing, you can pin exact versions if you wish:
```bash
pip freeze > requirements.txt
```

## Run

From the project root (the folder containing `app/`):
```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`.

## Test /health

**curl**
```bash
curl http://localhost:8000/health
```

**Expected response**
```json
{ "status": "ok", "timestamp": "<current ISO timestamp>" }
```

## Swagger docs

Open the interactive API documentation in a browser:
```
http://localhost:8000/docs
```

## Mid-Course Project — how to run

1. Backend: from the project root, activate the venv with `venv\Scripts\activate`, then run `uvicorn app.main:app --reload`. The API is at http://localhost:8000 and Swagger docs at http://localhost:8000/docs
2. Frontend: in a second terminal from the project root, run `python -m http.server 5500`, then open http://localhost:5500/frontend/index.html in a browser. The backend must be running first.
3. Tests: with the venv active, run `pytest -q` from the project root. Expected result: 28 passed.

This branch adds two features to the Module 1-3 Task Tracker: due dates with an overdue filter, and tags with a tag filter that combines with the overdue filter. See docs/midcourse/ for the user stories, the mini-ADR, the prompt log, verification evidence, and the reflection.
