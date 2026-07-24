"""API tests for the Task Tracker backend (Module 2, Part 2.4).

Sixteen named tests covering create, list, get-by-id, patch, transitions,
and delete. Uses the real in-memory storage with an autouse reset fixture.
"""

# ---------- POST /tasks ----------

def test_create_task_valid_returns_201_with_full_body(client):
    r = client.post("/tasks", json={"title": "Write report"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Write report"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["description"] == ""
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post("/tasks", json={"title": "ok", "priority": "Urgent"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post("/tasks", json={"title": "ok", "surprise": "nope"})
    assert r.status_code == 422


# ---------- GET /tasks ----------

def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    r = client.get("/tasks", params={"status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low one", "priority": "Low"})
    client.post("/tasks", json={"title": "high one", "priority": "High"})
    r = client.get("/tasks", params={"priority": "High"})
    assert r.status_code == 200
    bodies = r.json()
    assert len(bodies) == 1
    assert bodies[0]["priority"] == "High"


# ---------- GET /tasks/{id} ----------

def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    r = client.get("/tasks/missing-id")
    assert r.status_code == 404
    assert "detail" in r.json()


# ---------- PATCH /tasks/{id} ----------

def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"description": "updated desc"})
    assert r.status_code == 200
    body = r.json()
    assert body["description"] == "updated desc"
    assert body["title"] == created_task["title"]


def test_patch_not_found_returns_404(client):
    r = client.patch("/tasks/missing-id", json={"title": "x"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_returns_200(client, created_task):
    task_id = created_task["id"]
    # created task starts as ToDo; ToDo -> ToDo is allowed in this rule set
    r = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert r.status_code == 200


def test_patch_done_to_todo_returns_422(client, created_task):
    task_id = created_task["id"]
    # Move the task ToDo -> InProgress -> Done, then Done -> ToDo is NOT allowed
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    r = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert r.status_code == 422


# ---------- DELETE /tasks/{id} ----------

def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/missing-id")
    assert r.status_code == 404


# ---------- Module 3, Part 3.5: PATCH edge cases ----------

def test_patch_invalid_transition_inprogress_to_todo_returns_422(client):
    create = client.post("/tasks", json={"title": "Start work"})
    assert create.status_code == 201
    task = create.json()

    first = client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    assert first.status_code == 200
    assert first.json()["status"] == "InProgress"

    second = client.patch(f"/tasks/{task['id']}", json={"status": "ToDo"})
    assert second.status_code == 422
    assert "Invalid status transition" in second.json()["detail"]


def test_patch_unsupported_status_archived_returns_422(client):
    create = client.post("/tasks", json={"title": "Archive me"})
    assert create.status_code == 201
    task = create.json()

    response = client.patch(f"/tasks/{task['id']}", json={"status": "Archived"})
    assert response.status_code == 422

# ---------- Mid-Course Project, Feature 1: due dates + overdue ----------

def test_create_task_with_valid_due_date_returns_201_and_echoes_date(client):
    r = client.post("/tasks", json={"title": "Has a deadline", "due_date": "2030-01-15"})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == "2030-01-15"
    assert body["is_overdue"] is False


def test_create_task_with_invalid_due_date_format_returns_422(client):
    r = client.post("/tasks", json={"title": "Bad date", "due_date": "15-01-2030"})
    assert r.status_code == 422


def test_past_due_date_marks_task_overdue(client):
    r = client.post("/tasks", json={"title": "Late work", "due_date": "2020-01-01"})
    assert r.status_code == 201
    assert r.json()["is_overdue"] is True


def test_done_task_with_past_due_date_is_not_overdue(client):
    create = client.post("/tasks", json={"title": "Finished late", "due_date": "2020-01-01"})
    assert create.status_code == 201
    task_id = create.json()["id"]
    assert create.json()["is_overdue"] is True

    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    done = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert done.status_code == 200
    assert done.json()["status"] == "Done"
    assert done.json()["is_overdue"] is False


def test_create_task_with_tags_normalizes_and_deduplicates(client):
    r = client.post(
        "/tasks",
        json={"title": "Tagged work", "tags": ["  Alpha  ", "alpha", "Beta", "Gamma"]},
    )
    assert r.status_code == 201
    assert r.json()["tags"] == ["Alpha", "Beta", "Gamma"]


def test_create_task_with_blank_tag_returns_422(client):
    r = client.post("/tasks", json={"title": "Bare tag", "tags": ["ok", "   "]})
    assert r.status_code == 422


def test_create_task_with_six_tags_returns_422(client):
    r = client.post(
        "/tasks",
        json={"title": "Too many", "tags": ["a", "b", "c", "d", "e", "f"]},
    )
    assert r.status_code == 422


def test_patch_tags_replaces_existing_tags(client):
    create = client.post("/tasks", json={"title": "Retag me", "tags": ["old"]})
    assert create.status_code == 201
    task_id = create.json()["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"tags": ["new", "NEW", " fresh "]},
    )
    assert r.status_code == 200
    assert r.json()["tags"] == ["new", "fresh"]

def test_list_tasks_overdue_filter_returns_only_overdue_tasks(client):
    # Overdue: past due date, still ToDo
    overdue = client.post("/tasks", json={"title": "Late work", "due_date": "2020-01-01"})
    assert overdue.status_code == 201
    assert overdue.json()["is_overdue"] is True

    # Not overdue: future due date
    future = client.post("/tasks", json={"title": "Future work", "due_date": "2030-01-15"})
    assert future.status_code == 201

    # Not overdue: no due date at all
    client.post("/tasks", json={"title": "No deadline"})

    # Not overdue: past due date but Done
    done = client.post("/tasks", json={"title": "Finished late", "due_date": "2020-01-01"})
    done_id = done.json()["id"]
    client.patch(f"/tasks/{done_id}", json={"status": "InProgress"})
    client.patch(f"/tasks/{done_id}", json={"status": "Done"})

    # Without the filter, all four tasks come back
    unfiltered = client.get("/tasks")
    assert unfiltered.status_code == 200
    assert len(unfiltered.json()) == 4

    # With the filter, only the overdue one
    r = client.get("/tasks", params={"overdue": "true"})
    assert r.status_code == 200
    bodies = r.json()
    assert len(bodies) == 1
    assert bodies[0]["title"] == "Late work"
    assert bodies[0]["is_overdue"] is True
