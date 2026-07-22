# User Stories — Mid-Course Project

**Project:** Task Tracker (FastAPI + vanilla JS Kanban)
**Branch:** `mid-course-project`
**AI tool used:** GitHub Copilot Chat (VS Code)
**Features selected:** (1) Due dates + overdue filter, (2) Tags / labels

Stories were drafted with AI assistance, then reviewed and corrected.
Corrections are marked **[AI ASSUMPTION CORRECTED]**.

---

## Feature 1 — Due dates + overdue filter

### US-1.1 — Set a due date on a task
As a user, I want to assign a due date to a task so that I can see when it should be completed.

**Acceptance criteria**
- A task can be created or updated with an optional `due_date`.
- `due_date` is an ISO date string (`YYYY-MM-DD`) or `null`.
- The due date is displayed on the task card.
- An invalid date format returns **422** and the task is not created or updated.

> **[AI ASSUMPTION CORRECTED]** Copilot wrote only "the due date uses a valid date format" without specifying the format or the failure behaviour. That is untestable. This project already uses Pydantic v2 with `extra="forbid"` and returns 422 on validation failure, so the criterion was tightened to: ISO `YYYY-MM-DD`, nullable, invalid input returns 422.

### US-1.2 — Identify overdue tasks visually
As a user, I want overdue tasks to be visually identifiable so that I can spot late work quickly.

**Acceptance criteria**
- A task is overdue when its `due_date` is strictly before the current UTC date **and** its status is not `Done`.
- Overdue task cards show a distinct visual indicator.
- Tasks with `due_date = null` are never overdue.
- A completed (`Done`) task with a past due date is **not** overdue.

> **[AI ASSUMPTION CORRECTED]** Copilot defined overdue purely as "due date before today", which would flag finished work as overdue. A `Done` task is not outstanding, so status was added to the rule. Copilot also left "today" undefined; UTC date comparison was specified so tests are deterministic and do not depend on the machine's local timezone.

### US-1.3 — Filter the board to overdue tasks only
As a user, I want to filter the board to show only overdue tasks so that I can focus on urgent work.

**Acceptance criteria**
- The board header provides an "Overdue only" toggle.
- When active, only overdue tasks (per US-1.2) are rendered.
- All three status columns remain visible when the filter is active, showing the empty state if a column has no matches.
- Turning the filter off restores the full board.

> **[AI ASSUMPTION CORRECTED]** Copilot said non-matching tasks are "hidden" without saying what happens to a column that ends up empty. The Module 3 behaviour contract requires columns to stay visible in the empty state, so that rule was made explicit here.

### US-1.4 — Filter reflects edits
As a user, I want the overdue view to reflect my edits so that the board stays accurate.

**Acceptance criteria**
- Changing a due date from past to future removes the task from overdue results after the board reloads.
- Changing a due date from future to past adds it to overdue results after the board reloads.
- Dragging a task between columns does not break the filter.
- Dragging a task to `Done` removes it from overdue results after the board reloads.

> **[AI ASSUMPTION CORRECTED]** Copilot said results update "immediately", implying live sync. This frontend has no push mechanism; it re-fetches after a successful write. "Immediately" was replaced with "after the board reloads", which is what the code actually does and what a test can assert.

---

## Feature 2 — Tags / labels

### US-2.1 — Add tags to a task
As a user, I want to add tags to a task so that I can categorise it by theme.

**Acceptance criteria**
- A task can be created or updated with a list of tags.
- Each tag is trimmed of surrounding whitespace before storage.
- An empty or whitespace-only tag returns **422**.
- Duplicate tags are removed case-insensitively (`Bug` and `bug` collapse to one).
- More than **5** tags returns **422**.
- Omitting tags yields an empty list, not `null`.

> **[AI ASSUMPTION CORRECTED]** Copilot proposed tags with no validation whatsoever — no rule for empty strings, whitespace, duplicates, or a maximum count. The existing model already rejects whitespace-only titles, so tags were given equivalent validation: trim, reject blank with 422, de-duplicate case-insensitively, cap at 5.

### US-2.2 — See tags on the board
As a user, I want to see a task's tags on its card so that I can read context at a glance.

**Acceptance criteria**
- Tags render as chips on the card, below the title.
- A card with no tags renders no tag row and no empty container.
- Tag display does not push the title out of view or break the card layout.

### US-2.3 — Filter the board by tag
As a user, I want to filter tasks by tag so that I can view one category at a time.

**Acceptance criteria**
- The board header provides a tag filter control listing tags currently in use.
- When a tag is selected, only tasks carrying that tag are rendered.
- Tag matching is case-insensitive.
- The tag filter and the overdue filter combine with AND: with both active, only overdue tasks carrying the selected tag are shown.
- All three columns remain visible while filtering.

> **[AI ASSUMPTION CORRECTED]** Copilot treated the tag filter as independent and said nothing about combining it with the overdue filter, nor about case sensitivity. Since both features ship together, the combination rule was defined explicitly (AND), along with case-insensitive matching to match the de-duplication rule in US-2.1.

### US-2.4 — Edit tags on an existing task
As a user, I want to change a task's tags so that I can fix categorisation without recreating it.

**Acceptance criteria**
- Tags can be added, removed, or replaced from the edit modal.
- Saving with the tag field cleared results in an empty tag list and no chips on the card.
- The same validation as US-2.1 applies on edit; a blank tag returns 422 and the modal stays open with the server message visible.

> **[AI ASSUMPTION CORRECTED]** Copilot said "removing all tags leaves the task valid" but never said validation applies on update as well as create. Because `PATCH` is where the Module 3 hard gate already lives, edit-path validation was stated explicitly so it gets its own test.