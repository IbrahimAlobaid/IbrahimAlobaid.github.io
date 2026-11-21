"""Article 15 isolated diagnostic HTTP example, NOT a voice agent or production server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health/live":
            self.respond(200, {"status": "alive", "component": "training-demo"})
        elif self.path == "/health/ready":
            # Checks only the demonstration process; real dependencies require explicit checks.
            self.respond(200, {"status": "ready", "dependencies_checked": False})
        elif self.path == "/metrics":
            payload = b"# HELP training_demo_up Training HTTP example availability\n# TYPE training_demo_up gauge\ntraining_demo_up 1\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.respond(404, {"error": "not_found"})

    def respond(self, status, obj):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        # Do not write URL query strings, authorization headers, or payloads to logs.
        pass


def run():
    host = os.getenv("HEALTH_HOST", "127.0.0.1")
    port = int(os.getenv("HEALTH_PORT", "8105"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    run()
