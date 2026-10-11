"""Routing and validation. `handle` is the whole API; the HTTP server in __main__ only wraps it."""

import re

from api.store import NotFound, TaskStore

TASK_PATH = re.compile(r"^/tasks/(\d+)$")


def error(status, message):
    return status, {"error": message}


def validate_title(body):
    title = body.get("title") if isinstance(body, dict) else None
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


def handle(store, method, path, body=None):
    """Returns (status, json-serializable body)."""
    if path == "/health":
        print("health check called")
        return 200, {"status": "ok", "tasks": len(store.all())}

    if path == "/tasks":
        if method == "GET":
            return 200, store.all()
        if method == "POST":
            title = validate_title(body)
            if title is None:
                return error(400, "title is required")
            return 201, store.create(title)
        return error(405, "method not allowed")

    match = TASK_PATH.match(path)
    if not match:
        return error(404, "not found")
    task_id = int(match.group(1))
    try:
        if method == "GET":
            return 200, store.get(task_id)
        if method == "PATCH":
            changes = {}
            if isinstance(body, dict) and "title" in body:
                title = validate_title(body)
                if title is None:
                    return error(400, "title is required")
                changes["title"] = title
            if isinstance(body, dict) and "done" in body:
                if not isinstance(body["done"], bool):
                    return error(400, "done must be true or false")
                changes["done"] = body["done"]
            return 200, store.update(task_id, **changes)
        if method == "DELETE":
            store.delete(task_id)
            return 204, None
    except NotFound:
        return error(404, "no task with id {}".format(task_id))
    return error(405, "method not allowed")


def new_store():
    return TaskStore()
