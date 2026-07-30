# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes
- Docs-first / read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

AGENTS.md exists at the repository root and documents the tech stack (Python 3.11,
FastAPI, Pydantic v2, Uvicorn, pytest, httpx, vanilla JS), the Windows/CMD run and test
commands, the business rules as implemented in the code (statuses, priorities, title and
tag validation, status transitions including same-status no-ops), and the Module 5 / final
guardrails (docs-first, read-only by default, one task per thread, and no app/ or frontend/
changes unless explicitly approved and logged here).

## AI code review mini-log

The AI reviewed the files added on the final-project branch (AGENTS.md, .github/workflows/ci.yml,
Dockerfile, .dockerignore) and produced six comments. Each was graded by me.

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| CI triggers only on named branches (main, mid-course-project, final-project); a new branch would not run CI | Noise | Technically true, but triggering on the project branches is intentional and sufficient for this course project | No change |
| Add `--reload` to the Docker CMD so development is easier | Wrong | `--reload` is a development-only feature that the D1 Docker prompt explicitly forbids in the container; adding it would ship a dev setting into the runtime image | Rejected; CMD left without `--reload` |
| requirements.txt uses unpinned versions, so Docker and CI could install different versions on different days (non-reproducible) | Useful | A real reproducibility risk observed in the actual requirements.txt | Recorded as a backlog item; not changed for the final (out of scope) |
| .dockerignore excludes tests and docs, so pytest cannot run inside the image | Noise | True but correct by design; the container runs the app, tests run in CI | No change |
| AGENTS.md documents transition rules including same-status pairs as allowed (200), matching business_rules.py | Useful | Confirms the documentation is grounded in the actual code | Kept as-is; positive confirmation |
| Dockerfile copies only app/ and not frontend/, so the containerized app is broken | Wrong | Misreads the design; the frontend is served separately via python -m http.server, and the container ran successfully with /health returning 200 | Rejected |

Most important comment: I judged the `--reload` comment (graded Wrong) to be the most
important for a teammate to know about, because it is the one that sounds reasonable but
would actively break a correct decision if trusted. A confident-sounding AI comment is the
one most likely to cause harm.

## AI security mini-review

The AI performed a read-only security review of the app backend. Each finding was graded by me.

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| CORS allow_origins includes "null", a generally discouraged origin | app/main.py | Valid | Real observation; the "null" origin is present and is discouraged, though low risk for a local course app | Backlog note; review origins if the app is ever deployed |
| No authentication anywhere; anyone reachable can create, edit, or delete tasks | app/main.py (no auth code) | Valid | A real production risk, but an intentional course-scope decision documented in README and AGENTS.md ("no auth") | Accepted as course scope; would require auth before any real deployment |
| python-dotenv is listed as a dependency but never imported or used | requirements.txt, app/ | Valid | Confirmed unused; unused dependencies add needless surface area | Backlog: remove or document; left in place for the final |
| Data stored in a plain in-memory dict with no encryption at rest | app/storage.py | Valid | Unprotected data is a real concern worth noting, even if minor for this app | Not directly actionable on in-memory storage; would apply if a database is added later |
| title is capped at 200 characters but description has no maximum length (unbounded input) | app/models.py | Valid | Real, specific gap: _validate_title caps title, but description has no cap | Backlog: add a length limit on description |

## Manual security check

I checked the repository secrets handling myself, without copying any AI finding. I opened
.env.example directly and confirmed it contains only non-secret placeholder values
(PORT=8000, APP_ENV=development). I also confirmed that .env is listed in .gitignore, so a
real secrets file cannot be committed. No real credentials, tokens, or secrets are present
in the repository.

## One AI output I rejected or corrected

The AI review suggested adding `--reload` to the Docker container's CMD to make development
easier. I rejected this. `--reload` is a development-only feature that does not belong in a
container runtime image (the D1 Docker prompt explicitly forbids it), and adding it would
ship a development setting into the clean runtime image. I kept the CMD without `--reload`.

## Three AI usage rules

1. Never paste: real secrets, credentials, .env values, or tokens into an AI tool. Only
   placeholder config such as PORT=8000.
2. Always verify: any AI-generated command, config, or claim by running it myself (tests,
   Docker build, /health check) before trusting it.
3. Record AI contributions: by grading each AI comment or finding Useful/Noise/Wrong or
   Valid/False-Positive/Noise with a written reason, so it is clear what I accepted and what
   I rejected.

## Ownership statement

I am comfortable submitting this repository as my own work because I verified every piece of
it myself. I ran the tests and saw 29 pass, I built and ran the Docker container and confirmed
/health returned 200 and the container runs as a non-root user, and I watched the CI workflow
pass on GitHub. For every AI review comment and security finding, I decided myself whether it
was useful, valid, noise, or wrong, and I rejected the one suggestion (adding --reload to the
container) that would have broken a correct decision. Where I could not fully act on a finding,
such as encryption at rest on in-memory storage, I noted it honestly rather than pretending to
fix it. I can explain every file, command, and configuration choice in this repository.
