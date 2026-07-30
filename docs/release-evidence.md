# Release Evidence

## Baseline

- Branch: final-project (created from mid-course-project)
- Date: 2026-07-30
- Local app run command: `venv\Scripts\activate` then `uvicorn app.main:app --reload --port 8000`
- /health result: `GET /health` returned `200 OK` with body `{"status":"ok","timestamp":"2026-07-30T17:33:14.751726+00:00"}`
- Frontend check: served with `python -m http.server 5500` and opened at http://localhost:5500/frontend/index.html; the Kanban board and create/edit modal still render.
- Test command: `pytest -q`
- Test result: 29 passed (4 deprecation warnings, no failures)

## CI evidence

- Workflow file: .github/workflows/ci.yml
- Latest run link: https://github.com/hady151106-stack/task-tracker/actions/runs/30564266219
- Result: green (passed), commit 7f1f9da, ran in about 16 seconds on branch final-project
- Test command used by CI: `pytest -v`
- Shortcut check: no continue-on-error, no `|| true`, no `--exit-zero`; pytest runs directly and is not skipped; Python is pinned to 3.11.

## Docker evidence

- Build command: `docker build -t task-tracker:dev .`
- Build result: succeeded (14/14 steps)
- Run command: `docker run -d -p 8000:8000 --name tt-dev task-tracker:dev`
- Container status: `docker ps` showed `Up ... (healthy)`
- /health check: `curl -i http://localhost:8000/health` returned `HTTP/1.1 200 OK` with body `{"status":"ok","timestamp":"2026-07-30T17:33:14.751726+00:00"}`
- Non-root check: `docker exec tt-dev whoami` returned `app` (not root)
- No-baked-secrets check: .dockerignore excludes .env and .env.*; the Dockerfile copies only requirements.txt and the app/ source, never .env or credentials.
- Image size: 292MB on disk (python:3.11-slim multi-stage build)

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README says tests produce "29 passed" | Ran `pytest -q` on final-project | Accurate - 29 passed | None |
| requirements.txt lists python-dotenv as a dependency | Searched app/ for any dotenv import | Not actually used by the code | Noted as a finding in docs/final-ai-review.md; left in place |
| README run command was `uvicorn app.main:app --reload` (no port), while START_HERE.txt uses `--port 8000` | Compared README.md and START_HERE.txt | Inconsistency found between files | Fix planned: standardize on `--port 8000` during README update |
