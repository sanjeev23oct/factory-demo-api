# Checker: Section 2 — Backend (`api/app.py`, `README.md`)

Cat 1 checks. Run from the repository root.

```bash
grep -c 'def parse_due' api/app.py  # EXPECTED: 1
grep -c 'due must be a valid date in YYYY-MM-DD form' api/app.py  # EXPECTED: at least 2
grep -c 'urlsplit' api/app.py  # EXPECTED: at least 1
grep -c 'def handle(store, method, path, body=None, today=None)' api/app.py  # EXPECTED: 1
grep -c 'overdue' api/app.py  # EXPECTED: at least 2
grep -c 'due' README.md  # EXPECTED: at least 2
```
