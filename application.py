"""
Context Platform - Flask Application Entry Point
EB requires a file named application.py with an 'application' WSGI callable.

Streamlit runs on :8501 — nginx proxies /streamlit/ → :8501
A lock-file guard ensures only ONE Streamlit process ever starts,
even if gunicorn uses multiple workers or --preload triggers the
module twice.  start_new_session=True decouples Streamlit from gunicorn
so it keeps running if gunicorn restarts.
"""

import os
import sys
import fcntl
import subprocess
import socket
from flask import Flask, jsonify
from flask_cors import CORS

from api.context_routes import context_bp
from api.client_routes import clients_bp
from api.agent_routes import agents_bp
from api.upload_routes import uploads_bp

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
application = Flask(__name__)
CORS(application)

application.register_blueprint(context_bp)
application.register_blueprint(clients_bp)
application.register_blueprint(agents_bp)
application.register_blueprint(uploads_bp)


# ---------------------------------------------------------------------------
# Streamlit launcher — called at module import time (once per process)
# ---------------------------------------------------------------------------
def _port_in_use(port: int) -> bool:
    """Return True if something is already listening on the port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _start_streamlit():
    """
    Start Streamlit as an independent OS process.

    Guards:
    1. Port check  — skip if :8501 is already bound (another worker started it).
    2. Lock file   — /tmp/streamlit.lock prevents double-starts in race conditions.
    3. start_new_session=True — decouples Streamlit from gunicorn's process group
       so it survives gunicorn restarts without being sent SIGHUP/SIGTERM.
    """
    if _port_in_use(8501):
        print("[ContextOS] Streamlit already running on :8501 — skipping launch.")
        return

    lock_path = "/tmp/streamlit.lock"
    try:
        lock_fd = open(lock_path, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("[ContextOS] Another process holds the Streamlit lock — skipping.")
        return

    python_exec = sys.executable
    app_dir = os.path.dirname(os.path.abspath(__file__))

    cmd = [
        python_exec, "-m", "streamlit", "run",
        os.path.join(app_dir, "streamlit_app.py"),
        "--server.port",               "8501",
        "--server.headless",           "true",
        "--server.address",            "0.0.0.0",
        "--server.enableCORS",         "false",
        "--server.enableXsrfProtection", "false",
        # Tells Streamlit's JS to open WebSocket at /streamlit/_stcore/stream
        # instead of /_stcore/stream — fixes the endless "connecting" loop.
        "--server.baseUrlPath",        "streamlit",
        "--browser.gatherUsageStats",  "false",
    ]

    env = os.environ.copy()
    env["FLASK_API_URL"] = "http://localhost:8000"

    try:
        proc = subprocess.Popen(
            cmd,
            env=env,
            # Detach from gunicorn's process group — Streamlit survives gunicorn restarts
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        lock_fd.write(str(proc.pid))
        lock_fd.flush()
        print(f"[ContextOS] Streamlit launched — PID {proc.pid}")
        # Keep lock_fd open (held) for the life of this process
    except Exception as exc:
        print(f"[ContextOS] Failed to start Streamlit: {exc}")
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


_start_streamlit()


# ---------------------------------------------------------------------------
# Health check — EB load balancer pings /health
# ---------------------------------------------------------------------------
@application.route("/health", methods=["GET"])
def health():
    streamlit_up = _port_in_use(8501)
    return jsonify({
        "status":       "ok",
        "service":      "Context Platform API",
        "version":      "1.0.0",
        "streamlit":    "running" if streamlit_up else "starting",
    }), 200


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@application.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "Context Platform API",
        "version": "1.0.0",
        "endpoints": {
            "context":   "/api/v1/context/",
            "clients":   "/api/v1/clients/",
            "agents":    "/api/v1/agents/",
            "uploads":   "/api/v1/uploads/",
            "health":    "/health",
            "streamlit": "/streamlit/",
        }
    }), 200


# ---------------------------------------------------------------------------
# Local dev entry
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    application.run(host="0.0.0.0", port=port, debug=debug)
