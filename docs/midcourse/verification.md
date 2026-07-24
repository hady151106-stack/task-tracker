# Verification — Mid-Course Project

**Branch:** `mid-course-project`
**Environment:** Windows, Python 3.11, venv, FastAPI + pytest, frontend on port 5500, backend on port 8000.

## 1. Baseline (before any changes)

Captured immediately after creating the branch, before touching any source file.

pytest -q
20 passed, 4 warnings in 0.40s

The app was also checked manually: Swagger at localhost:8000/docs listed /health plus the five task endpoints, and the board at localhost:5500 rendered three columns in the empty state.

This baseline is the regression reference. Any later failure among these 20 tests would be a regression caused by my changes.

## 2. Backend test results

| Stage | Result |
|-------|--------|
| Baseline | 20 passed |
| After Feature 1 model change | 20 passed (no regression) |
| After Feature 1 tests added | 3 failed, 21 passed — see section 3 |
| After Feature 1 storage fix | 24 passed |
| After Feature 2 (tags) | 28 passed |
| After refactor | 28 passed |
| After overdue query filter added | 29 passed |

**Final suite: 29 passed** — the original 20 plus 9 new tests.

New tests, Feature 1:
- test_create_task_with_valid_due_date_returns_201_and_echoes_date
- test_create_task_with_invalid_due_date_format_returns_422
- test_past_due_date_marks_task_overdue
- test_done_task_with_past_due_date_is_not_overdue
- test_list_tasks_overdue_filter_returns_only_overdue_tasks

New tests, Feature 2:
- test_create_task_with_tags_normalizes_and_deduplicates
- test_create_task_with_blank_tag_returns_422
- test_create_task_with_six_tags_returns_422
- test_patch_tags_replaces_existing_tags

## 3. A real failure found by the tests

After adding the Feature 1 tests, three failed at once:

FAILED test_create_task_with_valid_due_date_returns_201_and_echoes_date - assert None == '2030-01-15'
FAILED test_past_due_date_marks_task_overdue - assert False is True
FAILED test_done_task_with_past_due_date_is_not_overdue - assert False is True
3 failed, 21 passed

**Diagnosis.** The first failure is the real one: due_date came back as None even though a valid date was posted. The other two are consequences — with due_date null, is_overdue correctly evaluates to False. One cause, three symptoms.

**Cause.** storage.add_task constructs TaskResponse field by field and had no due_date=payload.due_date line, so the field was silently dropped between the validated payload and storage. PATCH was unaffected because update_task uses model_copy(update=changes), which picks up any field generically.

**Fix.** Added the missing assignment in add_task — a cause fix. The symptom-suppression alternative (weakening the assertions to accept None) was rejected, since it would have left the field permanently unsaveable while the suite reported green.

**Result after fix:** 24 passed.

## 4. Break Test evidence

### Break Test 1 — the Done-exclusion rule

Target test: test_done_task_with_past_due_date_is_not_overdue

Rule broken: in TaskResponse.is_overdue, commented out the final clause `and self.status is not TaskStatus.DONE`

Result:

FAILED test_done_task_with_past_due_date_is_not_overdue - assert True is False
1 failed, 23 passed

Exactly one failure, and exactly the predicted one. With the clause removed, a completed task with a past due date is reported as overdue — the behaviour US-1.2 forbids. No other test failed, confirming the assertion is specific to this rule.

After restoring the line: 24 passed.

### Break Test 2 — the blank-tag rule

Target test: test_create_task_with_blank_tag_returns_422

Rule broken: in _validate_tags, commented out the blank check and its raise.

Result:

FAILED test_create_task_with_blank_tag_returns_422 - assert 201 == 422
1 failed, 27 passed

The whitespace-only tag was accepted and the task created with 201 instead of 422. The test detects the missing validation.

After restoring the lines: 28 passed.

## 5. Behaviour contract — before and after the refactor

The contract lives in BEHAVIOR_CONTRACT.md: C1-C8 from Module 3, plus C9-C14 added for this project.

**Refactor performed:** populateTagFilter in frontend/index.html. It previously read select.value at the start and assigned to the global tagFilter at the end, so the function both read and mutated global state through the DOM. It now reads tagFilter as the single source of truth, clears it when the selected tag no longer exists, and writes select.value from it.

**Checkpoint:** committed before the refactor was applied, so the working state was recoverable.

| ID | Behaviour | Before | After |
|----|-----------|--------|-------|
| C1 | Three columns render with correct counts | Pass | Pass |
| C2 | Cards sort High to Medium to Low | Pass | Pass |
| C3 | Loading skeletons appear | Pass | Pass |
| C4 | Empty columns stay visible | Pass | Pass |
| C5 | Error state with Retry when backend is stopped | Pass | Pass |
| C6 | Valid drag sends PATCH and updates the board | Pass | Pass |
| C7 | Invalid drag reverts and shows the server message | Pass | Pass |
| C8 | Modal flows including title validation and dismissal | Pass | Pass |
| C9 | Due date saves and displays | Pass | Pass |
| C10 | Past due date shows the Overdue pill | Pass | Pass |
| C11 | Done tasks are never overdue | Pass | Pass |
| C12 | Overdue filter hides non-overdue and keeps columns visible | Pass | Pass |
| C13 | Tags save, display as chips, and clear correctly | Pass | Pass |
| C14 | Tag filter combines with overdue filter using AND | Pass | Pass |

All fourteen behaviours held. The full pytest suite was re-run after the refactor: 28 passed.

## 6. Manual browser checks

Performed at localhost:5500 with the backend running and DevTools open.

Feature 1:
- Created a task with due date 2020-01-01 — card shows "Due 2020-01-01" and a red Overdue pill.
- Created a task with due date 2030-01-15 — due date shown, no Overdue pill.
- Ticked "Overdue only" — only the overdue card remained; all three columns stayed visible.
- Dragged the overdue task ToDo to InProgress to Done — the Overdue pill disappeared while the due date remained.

Feature 2:
- Created a task with tags "bug, urgent" — two chips rendered on the card.
- The tag dropdown populated with bug and urgent.
- Selecting bug filtered the board to that card, with all three columns still visible.
- With a task tagged docs and dated 2020-01-01, selecting docs AND ticking "Overdue only" kept the card visible, confirming AND combination; switching the dropdown to another tag hid it.
- Editing a card pre-filled the tags field comma-separated; clearing it and saving removed all chips.
- After removing the last remaining bug tag while bug was the active filter, the dropdown reset to "All tags" and the board returned to showing everything — the behaviour targeted by the refactor.

Regression spot-check: drag-and-drop, priority sorting, the empty state, and the modal's four dismissal paths were re-checked after every frontend change and continued to work.


## 7. Resubmission — backend overdue query filter

Facilitator feedback on the first submission identified that `GET /tasks?overdue=true` was not accepted by the endpoint: the parameter had no effect and a Done task with a past due date still appeared in the results. The brief lists an optional query filter for overdue as backend work, with a test confirming the filter returns only overdue tasks.

**Change.** Added an `overdue: bool = False` query parameter to `list_tasks` in `app/main.py`. When true, the route filters the list returned by `storage.get_all_tasks` down to tasks whose computed `is_overdue` field is true. The default of `False` leaves existing behaviour unchanged, so no previously passing test was affected.

**Test added.** `test_list_tasks_overdue_filter_returns_only_overdue_tasks` creates four tasks — one overdue, one with a future due date, one with no due date, and one with a past due date moved to Done — then asserts that the unfiltered list returns all four while `GET /tasks?overdue=true` returns only the overdue one.

**The test caught the bug before the fix landed.** On the first run it failed with `assert 4 == 1`: all four tasks came back. The cause was that the edit to `app/main.py` had not been saved to disk, so the route was still the original version. Confirmed by searching the file for `overdue` and finding no matches. After saving, the same test passed. The failure was useful — it proved the assertion is specific to the filter rather than passing regardless.

**Result:** 29 passed.

Also corrected in this resubmission: `README.md`, which still contained unmodified Module 1 skeleton text describing folders that were never built and stating that CRUD endpoints would be added in later modules. It now describes the project as it actually stands, including both mid-course features, the full route table, the real directory layout, and run instructions for the backend, the frontend, and the tests.