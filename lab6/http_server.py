#!/usr/bin/env python3
# Simple HTTP server for laboratory work: Content-Type/charset, gzip, cookie session, keep-alive
import gzip
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>OSI Lab</title></head>
<body>
<h1>OSI Model. Encapsulation</h1>
<p>HTTP Session: {sid}</p>
<p>Requests in session: {n}</p>
</body>
</html>
"""

SESSIONS = {}  # session id -> request count


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # allows Connection: keep-alive

    def do_GET(self):
        # --- session level: cookie ---
        sid = None
        for part in self.headers.get("Cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "session":
                sid = v
        new_session = sid not in SESSIONS
        if new_session:
            sid = uuid.uuid4().hex[:12]
            SESSIONS[sid] = 0
        SESSIONS[sid] += 1

        # --- presentation level: UTF-8 encoding and gzip compression ---
        body = PAGE.format(sid=sid, n=SESSIONS[sid]).encode("utf-8")
        use_gzip = "gzip" in self.headers.get("Accept-Encoding", "")
        if use_gzip:
            body = gzip.compress(body)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        if new_session:
            self.send_header("Set-Cookie", "session=%s; Path=/" % sid)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
