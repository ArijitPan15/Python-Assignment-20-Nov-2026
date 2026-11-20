"""A small notes API using Python's built-in HTTP server."""

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit


notes = []
next_note_id = 1


class NotesHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        self.request_started = time.perf_counter()
        self.response_status = 500
        try:
            super().handle_one_request()
        finally:
            if hasattr(self, "command") and hasattr(self, "path"):
                duration = time.perf_counter() - self.request_started
                print(f"{self.command} {self.path} {self.response_status} {duration:.4f}s", flush=True)

    def send_json(self, status: int, content=None):
        self.response_status = status
        self.send_response(status)
        if content is None:
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        response = json.dumps(content).encode("utf-8")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def get_note_id(self):
        path = urlsplit(self.path).path
        pieces = path.split("/")
        if len(pieces) == 3 and pieces[1] == "notes" and pieces[2].isdigit():
            return int(pieces[2])
        return None

    def find_note(self, note_id: int):
        for note in notes:
            if note["id"] == note_id:
                return note
        return None

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/notes":
            self.send_json(200, notes)
            return

        note_id = self.get_note_id()
        if note_id is not None:
            note = self.find_note(note_id)
            if note is not None:
                self.send_json(200, note)
            else:
                self.send_json(404, {"error": f"Note {note_id} not found"})
            return

        self.send_json(404, {"error": "Route not found"})

    def do_POST(self):
        global next_note_id

        path = urlsplit(self.path).path
        if path != "/notes":
            self.send_json(405 if self.get_note_id() is not None else 404,
                           {"error": "Method not allowed" if self.get_note_id() is not None else "Route not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                self.send_json(400, {"error": "Invalid request body length"})
                return
            body = self.rfile.read(length)
            note_data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})
            return

        if (not isinstance(note_data, dict)
                or not isinstance(note_data.get("text"), str)
                or not note_data["text"].strip()):
            self.send_json(400, {"error": "Note text is required"})
            return

        new_note = {"id": next_note_id, "text": note_data["text"]}
        notes.append(new_note)
        next_note_id += 1
        self.send_json(201, new_note)

    def do_DELETE(self):
        note_id = self.get_note_id()
        if note_id is None:
            path = urlsplit(self.path).path
            if path == "/notes":
                self.send_json(405, {"error": "Method not allowed"})
            else:
                self.send_json(404, {"error": "Route not found"})
            return

        note = self.find_note(note_id)
        if note is None:
            self.send_json(404, {"error": f"Note {note_id} not found"})
            return

        notes.remove(note)
        self.send_json(204)

    def method_not_allowed(self):
        path = urlsplit(self.path).path
        if path == "/notes" or self.get_note_id() is not None:
            self.send_json(405, {"error": "Method not allowed"})
        else:
            self.send_json(404, {"error": "Route not found"})

    do_PUT = method_not_allowed
    do_PATCH = method_not_allowed
    do_HEAD = method_not_allowed
    do_OPTIONS = method_not_allowed

    def log_message(self, format, *args):
        # The request timing log is printed in handle_one_request instead.
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("localhost", port), NotesHandler)
    print(f"Server running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server.server_close()
