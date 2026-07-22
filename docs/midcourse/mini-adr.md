# Mini-ADR — Mid-Course Project

**Status:** Accepted
**Date:** 2026-07-22
**Branch:** `mid-course-project`
**Scope:** Two features added to the Task Tracker built in Modules 1–3.

---

## Context

The Task Tracker after Module 3 is a FastAPI backend (Pydantic v2, `extra="forbid"`, in-memory storage, 5 CRUD routes, status-transition rules) plus a single-file vanilla JS Kanban frontend. 20 pytest tests pass at baseline.

Two features must be added end-to-end. At least one must be visible in the frontend. The constraint that dominates every decision below: each feature must be small enough to finish, verify, and explain. A polished, tested feature beats an ambitious partial one.

---

## Decision 1 — Feature selection

**Chosen:** Due dates + overdue filter, and Tags / labels.

Reasons:
- Both are visible in the Kanban UI, exceeding the "at least one visible" requirement.
- Both extend the existing `Task` model and the existing `POST` / `PATCH` / `GET` routes. No new route families, no new storage collections, no change to the status-transition rules.
- Both compose: a task can be overdue *and* tagged, so the two filters combine with AND. This is a small amount of extra design that makes the pair coherent rather than two unrelated additions.
- Both yield sharp 422 tests that mirror the validation patterns already proven in Modules 2–3.

**Rejected — Task comments.** Requires a second model, a second storage collection, at least three new routes, and 404 handling for missing parent tasks. Too much surface for the time available.

**Rejected — Activity log.** Requires an event record written from every mutating route, which means touching all five existing endpoints. High regression risk against a suite that currently passes 20/20.

**Rejected — Search + combined filters.** Overlaps heavily with the filtering work already implied by the two chosen features, so it would add query-parsing complexity without adding a distinct capability.

**Rejected — Bulk operations, saved views, frontend-only polish.** Named in the brief as bigger or easier to overbuild. Bulk operations in particular need multi-select state and partial-failure handling.

---

## Decision 2 — Where "overdue" is computed

**Chosen:** Compute overdue in the backend and expose it as a derived, read-only field on the task response.

Alternatives considered:
- **Compute in the frontend only.** Simpler, no backend change. Rejected: it cannot be unit-tested with pytest, and the brief requires backend test evidence.
- **Store `is_overdue` as a real field.** Rejected: it goes stale the moment the date rolls over, and it would be writable through `PATCH`, which contradicts `extra="forbid"` discipline.

Rule: a task is overdue when `due_date` is strictly before the current UTC date **and** `status != Done`. UTC is used so tests do not depend on the machine's local timezone.

---

## Decision 3 — Tag representation

**Chosen:** `tags: list[str]`, defaulting to an empty list, validated in the Pydantic model.

Validation: each tag is trimmed; blank or whitespace-only tags return 422; duplicates are removed case-insensitively; a maximum of 5 tags per task.

Alternatives considered:
- **Comma-separated string.** Rejected: pushes parsing into both the route and the frontend, and makes "reject empty tag" awkward to express.
- **A separate `Tag` model with its own ids and a join.** Rejected: normalisation is not warranted for in-memory storage and would require new routes, which is out of scope.
- **No maximum count.** Rejected: an unbounded list has no natural failure case to test and lets a single card break the board layout. A cap of 5 gives a clean 422 test.

---

## Decision 4 — Filtering location

**Chosen:** Filter on the client. `GET /tasks` continues to return all tasks; the board applies the overdue toggle and the tag filter during render.

Alternatives considered:
- **Query parameters on `GET /tasks` (`?overdue=true&tag=bug`).** Genuinely tempting and closer to real practice. Rejected for this project: it adds query-parameter validation, a new set of backend tests, and a round-trip on every filter toggle, while the dataset is small and held in memory. Client-side filtering keeps the diff small and keeps both filters in one place.

Consequence recorded honestly: if the dataset grew, this decision would need revisiting. It is correct for an in-memory tracker, not in general.

---

## Decision 5 — What is explicitly not being built

Rejected as out of scope, and recorded here so scope creep is visible if it happens later:

- Recurring or repeating due dates.
- Due-date reminders or notifications.
- Tag