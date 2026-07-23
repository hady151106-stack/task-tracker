# Module 3 — Behavior Contract (Part 3.4 deliverable)

Eight behaviors that must be TRUE before the refactor and still TRUE after it.
Check every one manually in the browser at `http://localhost:5500` with DevTools (F12) open.

| ID | Behavior | How to check manually | Pass/Fail |
|----|----------|----------------------|-----------|
| C1 | Three status columns render with correct counts | Open the board. You see ToDo, In Progress, Done. The number at the right of each column header equals the number of cards in it. | |
| C2 | Cards sort by priority inside each column | In a column with more than one card, High appears above Medium, and Medium above Low. | |
| C3 | Loading state appears before tasks load | In DevTools, Network tab, set throttling to "Slow 3G", then reload. Grey pulsing skeleton blocks appear before the cards. | |
| C4 | Empty columns remain visible | Delete or move all cards out of one column. The column stays on screen and shows a dashed box reading "Drop tasks here". | |
| C5 | Error state appears when the backend is stopped | Stop the uvicorn window (Ctrl+C), then reload the page. A red card appears saying "Could not load tasks" with a Retry button. Restart uvicorn and click Retry. | |
| C6 | Valid drag sends PATCH and updates the board | Drag a ToDo card to In Progress. Console logs `drop: updating task` then `drop: PATCH succeeded`. The card stays in the new column after the board refreshes. | |
| C7 | Invalid drag / server 422 reverts and shows the server message | Move a card all the way to Done, then drag it back to ToDo. Console logs `drop: PATCH failed with status 422`. The card jumps back to Done and a red banner appears at the top with the message "Invalid status transition from Done to ToDo...". | |
| C8 | New Task and Edit modal flows work, including title validation and dismissal | Click New Task, leave Title blank, click Save — "Title is required" shows and NO network request is sent. Type a title and Save — the card appears. Click Edit on a card — the form is pre-filled. Test all four dismissal paths: Cancel, the X button, the Escape key, and clicking the dark overlay outside the box. | |

## Mid-Course Project — Feature contract (C9-C14)

| ID | Behavior | How to check manually | Pass/Fail |
|----|----------|----------------------|-----------|
| C9 | Due date saves and displays | New Task with a due date. The card shows "Due YYYY-MM-DD". Edit the card and the date field is pre-filled. | |
| C10 | Past due date shows the Overdue pill | Create a task with due date 2020-01-01. The card shows a red "Overdue" pill next to the due date. | |
| C11 | Done tasks are never overdue | Take the overdue task and drag it ToDo to InProgress to Done. Once in Done, the Overdue pill disappears while the due date stays visible. | |
| C12 | Overdue-only filter hides non-overdue tasks and keeps columns visible | Tick "Overdue only". Only overdue cards remain. All three columns stay on screen, showing "Drop tasks here" where empty. Untick and the full board returns. | |
| C13 | Tags save, display as chips, and clear correctly | New Task with tags "bug, urgent". Two chips appear on the card. Edit the card, clear the tag field, Save. The chips disappear. | |
| C14 | Tag filter combines with the overdue filter using AND | Create a task with tag "docs" and due date 2020-01-01. Select "docs" in the tag dropdown AND tick "Overdue only". The card still shows. Change the tag dropdown to a different tag and the card disappears. | |

---

## Part 3.3 — the five modal flows (hard gate)

The instructor's gate: *"continue only when the invalid transition keeps the modal
open and shows a readable server error."*

| # | Flow | Expected behavior | Pass/Fail |
|---|------|-------------------|-----------|
| 1 | Empty title | Click New Task, leave Title empty (or type only spaces), click Save. Red message "Title is required" appears inside the modal. Check the Network tab — **no request was sent at all**. | |
| 2 | Create task | New Task, Title "Test high task", Priority High, Status ToDo, Save. Network shows `POST /tasks 201`. The modal closes and the card appears at the TOP of the ToDo column, above any Medium or Low card. | |
| 3 | Edit task | Click Edit on any card, change Priority from High to Low, Save. Network shows `PATCH /tasks/{id} 200`. The card moves to the bottom of its column. | |
| 4 | **Invalid transition (THE GATE)** | Take a card that is in **Done**. Click Edit. Change Status to **ToDo**. Click Save. Network shows `PATCH /tasks/{id} 422`. **The modal STAYS OPEN.** A readable red message appears inside it: "Invalid status transition from Done to ToDo. Allowed transitions: [...]". | |
| 5 | Dismissal | Open the modal, type something in Title, then close it with **Cancel**. Reopen it — the field is empty, not showing the old text. Repeat for the **X button**, the **Escape key**, and **clicking the dark overlay**. All four must close the modal and clear stale values. | |

---

## Valid vs invalid transitions in this build

This build uses the **instructor version** of `business_rules.py`.

| Move | Result |
|------|--------|
| ToDo → InProgress | 200 OK |
| InProgress → Done | 200 OK |
| Done → InProgress | 200 OK (reopen) |
| Same column → same column | No request is sent at all (frontend skips it) |
| **ToDo → Done** | **422 rejected** (cannot skip InProgress) |
| **Done → ToDo** | **422 rejected** (cannot revert to the beginning) |
| **InProgress → ToDo** | **422 rejected** (no backward transitions) |

Use **Done → ToDo** as your invalid-drag demo. That is the one shown in the video.
