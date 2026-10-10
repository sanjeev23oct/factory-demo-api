# Checker: Section 1 — Data

Cat 1 checks for `api/store.py`. Run from the repository root.

```bash
grep -c 'def create(self, title, due=None)' api/store.py  # EXPECTED: 1
grep -c '"due": due' api/store.py  # EXPECTED: 1
```
