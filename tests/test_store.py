import unittest

from api.store import NotFound, TaskStore


class TaskStoreTest(unittest.TestCase):
    def test_ids_increase_and_are_not_reused(self):
        store = TaskStore()
        first = store.create("a")
        store.delete(first["id"])
        self.assertEqual(store.create("b")["id"], first["id"] + 1)

    def test_get_unknown_raises(self):
        with self.assertRaises(NotFound):
            TaskStore().get(9)

    def test_returned_tasks_are_copies(self):
        store = TaskStore()
        task = store.create("a")
        task["title"] = "changed outside"
        self.assertEqual(store.get(task["id"])["title"], "a")
