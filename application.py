"""
Context Platform - Flask Application Entry Point
EB requires a file named application.py with an 'application' WSGI callable.

Streamlit is started independently by the EB post-deploy platform hook:
  .platform/hooks/postdeploy/01_start_streamlit.sh
It runs on port 8501; nginx proxies /streamlit/ → :8501
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
CORS(application)  # Allow Streamlit (same EB host, different port) to call Flask

# Register blueprints
application.register_blueprint(context_bp)
application.register_blueprint(clients_bp)
application.register_blueprint(agents_bp)
application.register_blueprint(uploads_bp)


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
