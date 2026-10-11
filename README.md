# factory-demo-api

A small tasks API, used to demonstrate the [software factory](https://github.com/sanjeev23oct/software-factory).
Standard library only, no dependencies.

    python3 -m api            # serves on http://127.0.0.1:8080
    python3 -m unittest discover -s tests

| Method | Path | Does |
| --- | --- | --- |
| GET | `/tasks` | List tasks |
| GET | `/tasks?overdue=true` | List tasks whose `due` is before today and not done |
| POST | `/tasks` | Create a task from `{"title": "...", "due": "YYYY-MM-DD"}` (`due` is optional) |
| GET | `/tasks/<id>` | Fetch one task |
| PATCH | `/tasks/<id>` | Update `title`, `done`, or `due` (`null` clears it) |
| DELETE | `/tasks/<id>` | Remove a task |

Errors are JSON: `{"error": "<message>"}` with a 4xx status.

`api/store.py` owns the data. `api/app.py` owns routing and validation and never touches storage directly.
