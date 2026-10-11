"""Routing and validation. `handle` is the whole API; the HTTP server in __main__ only wraps it."""

import datetime
import re
from urllib.parse import parse_qs, urlsplit

from api.store import NotFound, TaskStore

TASK_PATH = re.compile(r"^/tasks/(\d+)$")


def error(status, message):
    return status, {"error": message}


def validate_title(body):
    title = body.get("title") if isinstance(body, dict) else None
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


def parse_due(value):
    """Returns (ok, due) where due is a 'YYYY-MM-DD' str or None."""
    if value is None:
        return True, None
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return False, None
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False, None
    return True, value


def handle(store, method, path, body=None, today=None):
    """Returns (status, json-serializable body)."""
    today = today or datetime.date.today()
    split = urlsplit(path)
    path, query = split.path, parse_qs(split.query)
    if path == "/tasks":
        if method == "GET":
            overdue = query.get("overdue") == ["true"]
            if overdue:
                today_str = today.isoformat()
                return 200, [
                    task
                    for task in store.all()
                    if task["due"] is not None
                    and task["due"] < today_str
                    and task["done"] is False
                ]
            return 200, store.all()
        if method == "POST":
            title = validate_title(body)
            if title is None:
                return error(400, "title is required")
            due = None
            if isinstance(body, dict) and "due" in body:
                ok, due = parse_due(body["due"])
                if not ok:
                    return error(400, "due must be a valid date in YYYY-MM-DD form")
            return 201, store.create(title, due=due)
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
            if isinstance(body, dict) and "due" in body:
                ok, due = parse_due(body["due"])
                if not ok:
                    return error(400, "due must be a valid date in YYYY-MM-DD form")
                changes["due"] = due
            return 200, store.update(task_id, **changes)
        if method == "DELETE":
            store.delete(task_id)
            return 204, None
    except NotFound:
        return error(404, "no task with id {}".format(task_id))
    return error(405, "method not allowed")


def new_store():
    return TaskStore()
