"""In-memory task storage. Ids are permanent and never reused."""


class NotFound(Exception):
    pass


class TaskStore:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def all(self):
        return [dict(task) for task in self._tasks.values()]

    def get(self, task_id):
        if task_id not in self._tasks:
            raise NotFound(task_id)
        return dict(self._tasks[task_id])

    def create(self, title, due=None):
        task = {"id": self._next_id, "title": title, "done": False, "due": due}
        self._tasks[task["id"]] = task
        self._next_id += 1
        return dict(task)

    def update(self, task_id, **changes):
        if task_id not in self._tasks:
            raise NotFound(task_id)
        self._tasks[task_id].update(changes)
        return dict(self._tasks[task_id])

    def delete(self, task_id):
        if task_id not in self._tasks:
            raise NotFound(task_id)
        del self._tasks[task_id]
