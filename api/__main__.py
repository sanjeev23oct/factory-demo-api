import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from api.app import handle, new_store

STORE = new_store()


class Handler(BaseHTTPRequestHandler):
    def respond(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else None
        except ValueError:
            status, payload = 400, {"error": "body is not valid JSON"}
        else:
            status, payload = handle(STORE, self.command, self.path, body)
        data = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_PATCH = do_DELETE = respond


if __name__ == "__main__":
    print("tasks API on http://127.0.0.1:8080")
    HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
