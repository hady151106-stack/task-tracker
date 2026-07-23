# Prompt Log — Mid-Course Project

**AI tool:** GitHub Copilot Chat (VS Code, Copilot Free)
**Branch:** `mid-course-project`

Each entry records the prompt, what the assistant returned, and the decision:
**accepted**, **edited**, or **rejected**.

---

## Planning

### P0 — User stories for both features

**Prompt (abridged):** Described the existing Task model, Pydantic v2 with `extra="forbid"`, in-memory storage, and the vanilla JS board. Asked for 3–5 user stories per feature with testable acceptance criteria. Constrained it: no code, no features beyond the two chosen, no database, no auth, no notifications.

**Returned:** Eight well-formed stories, four per feature, all within scope. No code, no scope creep.

**Decision: edited.** The stories were structurally good but four assumptions were wrong for this project and were corrected in `user-stories.md`:
1. "Valid date format" was unspecified and therefore untestable → tightened to ISO `YYYY-MM-DD`, nullable, 422 on invalid.
2. Overdue was defined as "due date before today", which would flag completed work → added `status != Done`, and specified UTC so tests are deterministic.
3. Tags were proposed with no validation at all → added trim, blank rejection, case-insensitive de-duplication, and a cap of 5.
4. Filter results were said to update "immediately", implying live sync this frontend does not have → restated as "after the board reloads".

---

## Feature 1 — Due dates + overdue filter

### P1 — Backend model changes

**Prompt:** Add `due_date: Optional[date] = None` to `TaskCreate`, `TaskUpdate`, and `TaskResponse`. Add a `@computed_field` `is_overdue` on `TaskResponse` only, true when `due_date` is not None AND strictly before the current UTC date AND status is not `DONE`. Do not change any existing field, validator, or `model_config`. Do not add tags. Show only changed lines.

**Returned:** Correct edits — `date` and `computed_field` added to imports, field on all three models, computed property matching the rule exactly.

**Decision: accepted.** Verified rather than assumed: `self.status is not TaskStatus.DONE` uses identity comparison, which is only safe because `status` is annotated `TaskStatus` so Pydantic always coerces to the enum member. Had it been annotated `str`, a bare `"Done"` string would fail the identity check and every completed task would render as overdue.

**Process note:** the prompt asked for changed lines only; the assistant edited the file directly instead. The result was correct but arrived in a form I had not asked for, so the whole file had to be read to verify it.

### P2 — Frontend integration (weak prompt, then rewritten)

**Weak version (not used):**

> Add due dates to the board.

This is too vague to act on. It does not say which file, which elements, what the overdue rule is, where the filter belongs, or what must not change. An assistant answering it would have to invent the design, and any result would be unreviewable because there would be no stated intent to compare against.

**Rewritten version (used):** A numbered list of eight specific changes — five CSS classes, the filter-bar markup and its position, the date input in the modal, the `overdueOnly` variable, the exact filter expression to add to `renderBoard`, the signature and return contract of a `renderDates(task)` helper, the `openModal` and `saveTask` wiring, and the change handler. Closed with explicit non-goals: do not change drag-and-drop, sorting, modal dismissal, `escapeHtml`, or any existing behaviour.

**Returned:** All eight items implemented correctly — **and three structural HTML elements silently deleted**: the closing `</header>` tag, the entire `<main>` element containing `<section id="board">`, and the opening `<div id="modal-overlay">`. The summary claimed no unrelated behaviour was changed.

**Decision: edited (bug caught in review).** Inspecting `git diff` showed the deletions as `-` lines. Without the board section, `document.getElementById("board")` returns `null` and the first render throws — the page would have been completely broken. This was caught before running anything.

### P3 — Fixing the structural deletion

**Prompt:** Named the three deleted elements explicitly, stated the consequence (modal nested inside `<header>`, `getElementById("board")` returns null), specified exactly where each element must be restored, and constrained the fix: restore structure only, do not touch the filter-bar, the date input, the CSS, or any JavaScript.

**Returned:** All three elements restored in the correct positions.

**Decision: accepted after verification.** Re-ran `git diff` and confirmed the `-` lines were gone and `</header>`, `<main>`, and `div#modal-overlay` now appear as unchanged context. Verified in the browser afterwards.

**Lesson recorded:** the second prompt succeeded because it named the concrete symptom. A prompt of the form "it's broken, fix it" would not have constrained the fix.

---

## Feature 2 — Tags / labels

### P4 — Backend model changes

**Prompt:** Add `tags` to all three models with `Field(default_factory=list)`. Add a `_validate_tags` helper doing strip, blank rejection with a named error, case-insensitive de-duplication preserving first casing, and a maximum of 5. Wire `@field_validator("tags")` on `TaskCreate` and `TaskUpdate`, with `TaskUpdate` passing `None` through. No validator on `TaskResponse`. Change nothing else.

**Returned:** The helper and validators were correct, including the subtle ordering point that the cap is applied *after* de-duplication. It also correctly updated `storage.add_task` to persist tags.

**But it went outside scope:** it edited `tests/test_tasks.py` to add its own tests, and attempted to run `pytest` twice via the terminal, despite the prompt naming only `models.py`.

**Decision: partially rejected.** The `models.py` and `storage.py` changes were kept. The terminal commands were skipped both times — test runs are my verification step, and an assistant reporting its own pass result is not evidence. The two tests it wrote were reviewed individually and kept on their merits (they cover normalisation, de-duplication, and blank rejection, matching US-2.1), but two further tests were specified by me to cover the tag cap and the PATCH path, which its tests did not touch.

### P5 — Correcting the TaskUpdate annotation

**Prompt:** Pointed out that `TaskUpdate.tags` was annotated `list[str] = Field(default_factory=list)` while every other field on that model is `Optional` with a `None` default, and that its own validator already tested `if value is None` — so the annotation and the validator contradicted each other. Asked for that single line to become `Optional[list[str]] = None` and nothing else.

**Returned:** The single-line change.

**Decision: accepted.** Confirmed by `test_patch_tags_replaces_existing_tags` passing, which exercises the PATCH path for this field.

**How it was found:** reading the generated diff line by line. The code would have appeared to work in normal use because `model_dump(exclude_unset=True)` masks the problem for clients that omit the field.

### P6 — Frontend integration

**Prompt:** Nine numbered changes — two CSS classes plus the select styling, the `<select id="filter-tag">` inside the existing filter bar, the tags input in the modal, the `tagFilter` variable, the exact filter expression, a `renderTags(task)` helper with its empty-case contract, a `populateTagFilter()` that collects unique tags case-insensitively and preserves the current selection, the `openModal` and `saveTask` wiring, and the change handler. Non-goals restated, with an explicit instruction not to delete any HTML structural elements — added because of what happened in P2.

**Returned:** All nine items correct. No structural deletions this time.

**Decision: accepted after diff inspection.** Two observations recorded rather than changed: `renderTags` filters blank tags that the backend already rejects (harmless dead code), and `populateTagFilter` both read and wrote global state, which became the refactor target in P7.

### P7 — Focused refactor

**Prompt:** Refactor `populateTagFilter` only. Stated the problem precisely: it read `select.value` at the start and assigned to the global `tagFilter` at the end, so the function both read and mutated global state through the DOM, leaving the source of truth ambiguous. Specified the target behaviour: read the current selection from `tagFilter`, reset it to `""` if it no longer matches any existing tag, and set `select.value` from it. Behaviour must be identical.

**Returned:** Exactly that. The DOM read was removed, `tagFilter` became the single source of truth, and `select.value` is now written from it rather than read into it.

**Decision: accepted.** The diff touched only that one function. The behaviour contract (C1–C14) was re-verified in the browser afterwards and the full pytest suite re-run.

---

## Summary of decisions

| Prompt | Scope | Decision |
|--------|-------|----------|
| P0 | User stories | Edited — four assumptions corrected |
| P1 | `models.py` due_date | Accepted after verification |
| P2 | Frontend due dates | Edited — caught three deleted HTML elements |
| P3 | Structural fix | Accepted after verification |
| P4 | `models.py` tags | Partially rejected — kept source edits, skipped its terminal runs, supplemented its tests |
| P5 | `TaskUpdate` annotation | Accepted |
| P6 | Frontend tags | Accepted after diff inspection |
| P7 | Refactor | Accepted |