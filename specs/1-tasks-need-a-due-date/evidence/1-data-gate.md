Status: PASS

| Check | Expected | Actual | Result |
|---|---|---|---|
| Cat 1: `grep -c 'def create(self, title, due=None)' api/store.py` | 1 | 1 | PASS |
| Cat 1: `grep -c '"due": due' api/store.py` | 1 | 1 | PASS |
| Design: `TaskStore.create` signature is exactly `create(self, title, due=None)` | signature matches | `api/store.py:21`: `def create(self, title, due=None):` — exact match | PASS |
| Design: stored/returned task dict is `{"id": ..., "title": title, "done": False, "due": due}` | dict literal matches | `api/store.py:22`: `task = {"id": self._next_id, "title": title, "done": False, "due": due}` — exact match | PASS |
| Design: existing call sites passing only `title` still work | `due` defaults to `None`, no caller breaks | `api/app.py:30` calls `store.create(title)` (Section 2 not yet wired); `due=None` default fills in `due: None` automatically; `tests/test_app.py:16` asserts `{"id": 1, "title": "buy milk", "done": False, "due": None}` and passes | PASS |
| Design: `TaskStore.update` is unchanged | byte-identical to pre-feature version | Diffed current `api/store.py:27-31` against `git show 0ecfdd4:api/store.py` — `update` method body is byte-for-byte identical | PASS |
| Cat 3: `python3 -m unittest discover -s tests` | all tests pass, no regressions | `Ran 9 tests in 0.000s` — `OK` (all 9 tests pass: 6 in `test_app.py`, 3 in `test_store.py`) | PASS |
