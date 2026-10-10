Status: FAIL

# Section 1 — Data (api/store.py) — Gate Evidence

| Check | Expected | Actual | Result |
|---|---|---|---|
| Cat 1: `grep -c 'def create(self, title, due=None)' api/store.py` | `1` | `1` | PASS |
| Cat 1: `grep -c '"due": due' api/store.py` | `1` | `1` | PASS |
| Cat 3: `python3 -m unittest discover -s tests` | all pass, no regressions | `Ran 9 tests in 0.001s` — `FAILED (failures=1)`; `test_create_then_list` (tests/test_app.py) fails: `assertEqual(task, {"id": 1, "title": "buy milk", "done": False})` vs actual `{'id': 1, 'title': 'buy milk', 'done': False, 'due': None}` | FAIL |
| Design: `TaskStore.create` signature is exactly `create(self, title, due=None)` | matches `design.md` § Data | `api/store.py:21`: `def create(self, title, due=None):` | PASS |
| Design: stored/returned task dict is `{"id": ..., "title": title, "done": False, "due": due}` | matches | `api/store.py:22`: `task = {"id": self._next_id, "title": title, "done": False, "due": due}` | PASS |
| Design: existing call sites passing only `title` still work (`due` defaults to `None`) | works | `api/app.py:30` calls `store.create(title)`; signature default `due=None` makes this work — confirmed by direct call, but this behavior change (now always including a `due` key) breaks an existing test that asserted the old dict shape (see Cat 3 row) | PASS (signature) / regression surfaced in Cat 3 |
| Design: `TaskStore.update` unchanged, `due` flows through existing `**changes` mechanism | unchanged | `api/store.py:27-31` identical to pre-change `update(self, task_id, **changes)`; no special-casing of `due` | PASS |
| `api/app.py` still calls `store.create(title)` only (Section 2 not yet touched) | unaffected | `api/app.py:30`: `return 201, store.create(title)` — single positional arg, no `due` wiring yet | PASS |

## Summary

Both Cat 1 grep checks match their EXPECTED values (`1` and `1`), and the `api/store.py` code matches the design requirements for `TaskStore.create`/`TaskStore.update` exactly: signature `create(self, title, due=None)`, dict shape `{"id": ..., "title": title, "done": False, "due": due}`, and `update` is untouched.

However, the Cat 3 full test-suite run does **not** pass: `tests/test_app.py::test_create_then_list` fails because it asserts the POST-response task dict equals `{"id": 1, "title": "buy milk", "done": False}` (no `due` key), while the Section 1 change to `api/store.py` now always includes `"due": None` in every created task. This is a real regression introduced by the Section 1 change against the pre-existing test suite (Section 3, which would update/extend tests for `due`, has not run yet). Per the gate instructions this is graded as-is even though Section 3 is expected to fix it later — the gate for Section 1 alone requires the full suite to pass with no regressions, and it currently does not.

**Overall Status: FAIL** (Cat 3 check fails; Cat 1 and design-requirement checks pass).
