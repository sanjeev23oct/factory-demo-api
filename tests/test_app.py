import datetime
import unittest

from api.app import handle, new_store


class AppTest(unittest.TestCase):
    def setUp(self):
        self.store = new_store()

    def call(self, method, path, body=None, today=None):
        return handle(self.store, method, path, body, today=today)

    def test_create_then_list(self):
        status, task = self.call("POST", "/tasks", {"title": "  buy milk "})
        self.assertEqual(status, 201)
        self.assertEqual(task, {"id": 1, "title": "buy milk", "done": False, "due": None})
        self.assertEqual(self.call("GET", "/tasks"), (200, [task]))

    def test_create_without_title_is_rejected(self):
        self.assertEqual(self.call("POST", "/tasks", {"title": " "}), (400, {"error": "title is required"}))

    def test_mark_done(self):
        self.call("POST", "/tasks", {"title": "a"})
        status, task = self.call("PATCH", "/tasks/1", {"done": True})
        self.assertEqual((status, task["done"]), (200, True))

    def test_done_must_be_boolean(self):
        self.call("POST", "/tasks", {"title": "a"})
        self.assertEqual(self.call("PATCH", "/tasks/1", {"done": "yes"})[0], 400)

    def test_unknown_task(self):
        self.assertEqual(self.call("GET", "/tasks/9"), (404, {"error": "no task with id 9"}))

    def test_delete(self):
        self.call("POST", "/tasks", {"title": "a"})
        self.assertEqual(self.call("DELETE", "/tasks/1"), (204, None))
        self.assertEqual(self.call("GET", "/tasks"), (200, []))

    # 3.2.1 — POST /tasks with/without/null due

    def test_create_with_valid_due(self):
        status, task = self.call("POST", "/tasks", {"title": "a", "due": "2026-11-01"})
        self.assertEqual(status, 201)
        self.assertEqual(task["due"], "2026-11-01")

    def test_create_without_due_key(self):
        status, task = self.call("POST", "/tasks", {"title": "a"})
        self.assertEqual(status, 201)
        self.assertIsNone(task["due"])

    def test_create_with_explicit_null_due(self):
        status, task = self.call("POST", "/tasks", {"title": "a", "due": None})
        self.assertEqual(status, 201)
        self.assertIsNone(task["due"])

    # 3.2.2 — due present on GET list, GET by id, and PATCH responses

    def test_get_tasks_list_includes_due(self):
        self.call("POST", "/tasks", {"title": "a"})
        status, tasks = self.call("GET", "/tasks")
        self.assertEqual(status, 200)
        self.assertIn("due", tasks[0])
        self.assertIsNone(tasks[0]["due"])

    def test_get_task_by_id_includes_due(self):
        self.call("POST", "/tasks", {"title": "a"})
        status, task = self.call("GET", "/tasks/1")
        self.assertEqual(status, 200)
        self.assertIn("due", task)
        self.assertIsNone(task["due"])

    def test_patch_response_includes_due_for_task_never_given_one(self):
        self.call("POST", "/tasks", {"title": "a"})
        status, task = self.call("PATCH", "/tasks/1", {"done": True})
        self.assertEqual(status, 200)
        self.assertIn("due", task)
        self.assertIsNone(task["due"])

    # 3.2.3 — PATCH sets, clears, leaves due unchanged; unknown id still 404

    def test_patch_sets_new_due(self):
        self.call("POST", "/tasks", {"title": "a"})
        status, task = self.call("PATCH", "/tasks/1", {"due": "2026-12-25"})
        self.assertEqual(status, 200)
        self.assertEqual(task["due"], "2026-12-25")

    def test_patch_clears_due_with_null(self):
        self.call("POST", "/tasks", {"title": "a", "due": "2026-12-25"})
        status, task = self.call("PATCH", "/tasks/1", {"due": None})
        self.assertEqual(status, 200)
        self.assertIsNone(task["due"])

    def test_patch_leaves_due_unchanged_when_omitted(self):
        self.call("POST", "/tasks", {"title": "a", "due": "2026-12-25"})
        status, task = self.call("PATCH", "/tasks/1", {"title": "b"})
        self.assertEqual(status, 200)
        self.assertEqual(task["due"], "2026-12-25")

    def test_patch_unknown_id_with_valid_due_returns_404(self):
        self.assertEqual(
            self.call("PATCH", "/tasks/9", {"due": "2026-12-25"}),
            (404, {"error": "no task with id 9"}),
        )

    # 3.2.4 — invalid due is rejected on both POST and PATCH, state unchanged

    INVALID_DUE_VALUES = ["2026-13-01", "2026-02-30", "11/01/2026", 20261101, ""]

    def test_post_with_invalid_due_is_rejected(self):
        for value in self.INVALID_DUE_VALUES:
            with self.subTest(value=value):
                status, body = self.call("POST", "/tasks", {"title": "a", "due": value})
                self.assertEqual(status, 400)
                self.assertEqual(body, {"error": "due must be a valid date in YYYY-MM-DD form"})
                self.assertEqual(self.call("GET", "/tasks"), (200, []))

    def test_patch_with_invalid_due_is_rejected(self):
        for value in self.INVALID_DUE_VALUES:
            with self.subTest(value=value):
                self.store = new_store()
                self.call("POST", "/tasks", {"title": "a", "due": "2026-01-01"})
                status, body = self.call("PATCH", "/tasks/1", {"due": value})
                self.assertEqual(status, 400)
                self.assertEqual(body, {"error": "due must be a valid date in YYYY-MM-DD form"})
                _, task = self.call("GET", "/tasks/1")
                self.assertEqual(task["due"], "2026-01-01")

    # 3.2.5 — GET /tasks?overdue=true filtering with a fixed today

    def test_overdue_includes_task_due_before_today_and_not_done(self):
        today = datetime.date(2026, 6, 15)
        self.call("POST", "/tasks", {"title": "a", "due": "2026-06-14"})
        status, tasks = self.call("GET", "/tasks?overdue=true", today=today)
        self.assertEqual(status, 200)
        self.assertEqual([task["id"] for task in tasks], [1])

    def test_overdue_excludes_task_due_exactly_today(self):
        today = datetime.date(2026, 6, 15)
        self.call("POST", "/tasks", {"title": "a", "due": "2026-06-15"})
        status, tasks = self.call("GET", "/tasks?overdue=true", today=today)
        self.assertEqual((status, tasks), (200, []))

    def test_overdue_excludes_done_task_even_if_overdue(self):
        today = datetime.date(2026, 6, 15)
        self.call("POST", "/tasks", {"title": "a", "due": "2026-06-14"})
        self.call("PATCH", "/tasks/1", {"done": True})
        status, tasks = self.call("GET", "/tasks?overdue=true", today=today)
        self.assertEqual((status, tasks), (200, []))

    def test_overdue_excludes_task_with_no_due(self):
        today = datetime.date(2026, 6, 15)
        self.call("POST", "/tasks", {"title": "a"})
        status, tasks = self.call("GET", "/tasks?overdue=true", today=today)
        self.assertEqual((status, tasks), (200, []))

    def test_get_tasks_without_overdue_param_returns_everything(self):
        today = datetime.date(2026, 6, 15)
        self.call("POST", "/tasks", {"title": "a", "due": "2026-06-14"})
        self.call("POST", "/tasks", {"title": "b", "due": "2026-06-15"})
        self.call("POST", "/tasks", {"title": "c"})
        self.call("PATCH", "/tasks/1", {"done": True})
        status, tasks = self.call("GET", "/tasks", today=today)
        self.assertEqual(status, 200)
        self.assertEqual([task["id"] for task in tasks], [1, 2, 3])
