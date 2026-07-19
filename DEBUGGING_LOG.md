# Module 3 — Debugging Log and Reflection (R1 deliverable)

---

## Debugging log — four lines (Break Test)

**1. Bug or failure**
I commented out the `validate_status_transition(existing.status, payload.status)` call
in the PATCH route in `app/main.py`, removing the status-transition business rule while
leaving every other behavior in place.

**2. Evidence**
`pytest tests/ -v` — three tests failed:
`test_patch_invalid_transition_todo_to_done_returns_422`,
`test_patch_done_to_todo_returns_422`, and
`test_patch_invalid_transition_inprogress_to_todo_returns_422`.
Each failed on the same assertion line with `assert 200 == 422`: the API accepted an
invalid backward transition and returned the updated task instead of rejecting it.

**3. AI diagnosis**
Root cause was the removed validator call in the PATCH route, not the tests. Nothing
else in the request path checks the `(current, new)` status pair — Pydantic only
confirms that the submitted value is a valid `TaskStatus` enum member, which "ToDo"
always is. With the validator commented out, `storage.update_task` writes the new
status unconditionally and the route returns 200.

**4. Decision**
Accepted as a **cause fix**: restore the `validate_status_transition` call in the PATCH
route. Rejected the symptom-suppression alternative of changing the assertions from 422
to 200, which would have made the suite green while leaving the business rule missing.
After restoring the line, `pytest tests/ -v` returned 20 passed.

---

## Reflection log — 3 to 5 sentences

The AI assistant was fastest at the repetitive frontend layers: it produced the CSS
design system and the column/card rendering markup far quicker than writing them by
hand, and it correctly preserved the class names and `data-status` attributes the later
drag-and-drop code depended on. I had to constrain it in two places — it proposed a
tiebreaker of `a.id - b.id` for cards of equal priority, which silently evaluates to
`NaN` because our task ids are UUID strings rather than numbers, and after the CSS
refactor it offered to add avatars, status chips, and a floating action button that I
had never asked for and declined. Working from evidence rather than description changed
the outcome repeatedly: the DevTools Console showing `drop: PATCH failed with status 422`
told me the rollback path was firing correctly, and the uvicorn log showing `OPTIONS`
preflight requests confirmed CORS was configured rather than merely assumed. The habit I
will carry into later modules is constraining a refactor by **selecting the exact section
first** — selecting only the `<style>` block made it structurally impossible for the
assistant to touch the fetch logic, drag handlers, or modal behavior, which is far more
reliable than asking it politely not to.

---

## Instances where I caught the AI (conclusion-video deliverables)

**1. A UI state was going to be skipped.**
The first pass of the board rendering handled only *loading*, *ready*, and *error*.
The **empty** state — a column with zero cards still rendering with a visible
"Drop tasks here" placeholder — had to be required explicitly, otherwise an empty
column would have collapsed and been unusable as a drop target later.

**2. The AI tried to change things I did not ask for.**
After the CSS refactor it volunteered: *"If you want, I can also enhance the task cards
with avatars, status chips, or a floating action button."* None of that was in the
behavior contract. I declined and kept the refactor to CSS only.

**3. A generated tiebreaker was wrong for our data.**
`return a.id - b.id` as the equal-priority tiebreaker produces `NaN` for UUID string
ids, which makes the sort order unstable and lets cards jump around unpredictably.
Replaced with `String(a.id).localeCompare(String(b.id))`, which sorts ids ascending
correctly for string ids.

---

## Prompts used (from the Module 3 Prompt Library)

| Prompt | Purpose | Where |
|---|---|---|
| P1 | Verify the assistant reads `app/main.py`; confirm CORS "not present" | Part 3.1 |
| P2 | Ask for a build plan before any code | Part 3.2 |
| B1 | Static Kanban layout, three columns, `data-status` exact values | Part 3.2 |
| B2 | `fetchTasks()` / `renderBoard()`, priority sort, no drag yet | Part 3.2 |
| B3 | Loading, ready, empty, and error states | Part 3.2 |
| B4 | CORS middleware from DevTools evidence | Part 3.2 |
| B5 | Native drag-and-drop, PATCH, optimistic update, rollback on 422 | Part 3.2 |
| C2 | Create/edit modal, title trim, POST/PATCH, 422 handling, dismissal | Part 3.3 |
| D1 | The 8-item behavior contract | Part 3.4 |
| D2 | Refactor one selected section only (the `<style>` block) | Part 3.4 |
| D4 | Surgical recovery template for a single regression | Part 3.4 |
| E1 | Brainstorm six PATCH edge cases, no code | Part 3.5 |
| E2 | Write ONE pytest test for one scenario | Part 3.5 |
| E3 | Prove the test by deliberate source breakage | Part 3.5 |
| E4 | Diagnose the pytest failure, cause fix vs symptom suppression | Part 3.5 |
| R1 | This debugging log and reflection | Deliverable |

---

## D4 — recovery template (keep for the refactor)

```
After the refactor, [describe the broken behavior].

Before the refactor, this behavior worked.
Restore that behavior in the selected function or section only.
Do not touch unrelated code.
Do not rewrite the full file.
```
