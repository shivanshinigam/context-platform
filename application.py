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
# Health check — EB load balancer pings /health
# ---------------------------------------------------------------------------
@application.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":       "ok",
        "service":      "Context Platform API",
        "version":      "1.0.0"
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
