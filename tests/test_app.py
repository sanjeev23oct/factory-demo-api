import unittest

from api.app import handle, new_store


class AppTest(unittest.TestCase):
    def setUp(self):
        self.store = new_store()

    def call(self, method, path, body=None):
        return handle(self.store, method, path, body)

    def test_create_then_list(self):
        status, task = self.call("POST", "/tasks", {"title": "  buy milk "})
        self.assertEqual(status, 201)
        self.assertEqual(task, {"id": 1, "title": "buy milk", "done": False})
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
