"""
Context Platform - Client Management API Routes
Register clients, list clients, get client details.
No DB yet — in-memory store.
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify

clients_bp = Blueprint("clients", __name__, url_prefix="/api/v1/clients")

# ---------------------------------------------------------------------------
# In-memory stub store
# ---------------------------------------------------------------------------
_clients_store: dict = {}


# ---------------------------------------------------------------------------
# POST /api/v1/clients/register
# ---------------------------------------------------------------------------
@clients_bp.route("/register", methods=["POST"])
def register_client():
    """
    Register a new client on the Context Platform.
    Expected JSON body:
    {
        "name": "Acme Corp",
        "email": "admin@acme.com",
        "industry": "retail",
        "aws_account_id": "123456789012",     # client's own AWS account
        "aws_region": "us-east-1",
        "plan": "starter"                     # starter | pro | enterprise
    }
    """
    body = request.get_json(silent=True) or {}

    name = body.get("name")
    email = body.get("email")

    if not name or not email:
        return jsonify({
            "success": False,
            "error": "name and email are required"
        }), 400

    client_id = "client_" + str(uuid.uuid4()).replace("-", "")[:12]
    client = {
        "client_id": client_id,
        "name": name,
        "email": email,
        "industry": body.get("industry", "unknown"),
        "aws_account_id": body.get("aws_account_id", ""),
        "aws_region": body.get("aws_region", "us-east-1"),
        "plan": body.get("plan", "starter"),
        "status": "active",
        "registered_at": datetime.utcnow().isoformat(),
        "context_count": 0
    }
    _clients_store[client_id] = client

    return jsonify({
        "success": True,
        "client_id": client_id,
        "message": f"Client '{name}' registered successfully",
        "client": client
    }), 201


# ---------------------------------------------------------------------------
# GET /api/v1/clients
# ---------------------------------------------------------------------------
@clients_bp.route("/", methods=["GET"])
def list_clients():
    """List all registered clients."""
    clients = list(_clients_store.values())
    return jsonify({
        "success": True,
        "count": len(clients),
        "clients": clients
    }), 200


# ---------------------------------------------------------------------------
# GET /api/v1/clients/<client_id>
# ---------------------------------------------------------------------------
@clients_bp.route("/<client_id>", methods=["GET"])
def get_client(client_id):
    """Get a single client by ID."""
    client = _clients_store.get(client_id)
    if not client:
        return jsonify({"success": False, "error": "Client not found"}), 404

    return jsonify({"success": True, "client": client}), 200


# ---------------------------------------------------------------------------
# PATCH /api/v1/clients/<client_id>/status
# ---------------------------------------------------------------------------
@clients_bp.route("/<client_id>/status", methods=["PATCH"])
def update_client_status(client_id):
    """Activate or deactivate a client."""
    client = _clients_store.get(client_id)
    if not client:
        return jsonify({"success": False, "error": "Client not found"}), 404

    body = request.get_json(silent=True) or {}
    new_status = body.get("status")

    if new_status not in ("active", "inactive", "suspended"):
        return jsonify({
            "success": False,
            "error": "status must be one of: active, inactive, suspended"
        }), 400

    client["status"] = new_status
    client["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({
        "success": True,
        "message": f"Client status updated to '{new_status}'",
        "client": client
    }), 200
