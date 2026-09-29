"""
Context Platform - Flask Application Entry Point
EB requires a file named application.py with an 'application' WSGI callable.
"""

import os
import subprocess
import threading
import sys
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
CORS(application)  # Allow Streamlit (same EB host, different port) to call Flask

# Register blueprints
application.register_blueprint(context_bp)
application.register_blueprint(clients_bp)
application.register_blueprint(agents_bp)
application.register_blueprint(uploads_bp)


# ---------------------------------------------------------------------------
# Start Streamlit as a background subprocess
# Runs on port 8501; nginx proxies /streamlit/ → :8501
# ---------------------------------------------------------------------------
def _start_streamlit():
    """Launch Streamlit in a background thread when gunicorn starts Flask."""
    python_exec = sys.executable  # same venv python that runs Flask
    streamlit_cmd = [
        python_exec, "-m", "streamlit", "run",
        os.path.join(os.path.dirname(__file__), "streamlit_app.py"),
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.address", "0.0.0.0",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ]
    env = os.environ.copy()
    env["FLASK_API_URL"] = "http://localhost:8000"  # gunicorn port on EB
    try:
        subprocess.Popen(streamlit_cmd, env=env)
    except Exception as e:
        print(f"[ContextOS] Streamlit failed to start: {e}")


# Start Streamlit once — guard against multiple gunicorn workers both starting it
_streamlit_started = False
if not _streamlit_started:
    _streamlit_started = True
    _t = threading.Thread(target=_start_streamlit, daemon=True)
    _t.start()


# ---------------------------------------------------------------------------
# Health check — EB load balancer pings this
# ---------------------------------------------------------------------------
@application.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "Context Platform API",
        "version": "1.0.0"
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
            "context":  "/api/v1/context/",
            "clients":  "/api/v1/clients/",
            "agents":   "/api/v1/agents/",
            "uploads":  "/api/v1/uploads/",
            "health":   "/health"
        }
    }), 200


# ---------------------------------------------------------------------------
# Dev server entry
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    application.run(host="0.0.0.0", port=port, debug=debug)
