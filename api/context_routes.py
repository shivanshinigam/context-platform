"""
Context Platform - Context API Routes
Handles context data: upload, list, retrieve, delete
No DB yet — in-memory store used as stub.
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify

context_bp = Blueprint("context", __name__, url_prefix="/api/v1/context")

# ---------------------------------------------------------------------------
# In-memory stub store (replace with DynamoDB / RDS later)
# ---------------------------------------------------------------------------
_context_store: dict = {}


# ---------------------------------------------------------------------------
# POST /api/v1/context/upload
# ---------------------------------------------------------------------------
@context_bp.route("/upload", methods=["POST"])
def upload_context():
    """
    Client uploads context data.
    Expected JSON body:
    {
        "client_id": "client_abc",
        "context_type": "product_catalog",
        "data": { ... },
        "tags": ["ecommerce", "retail"],
        "aws_region": "us-east-1"
    }
    """
    body = request.get_json(silent=True) or {}

    client_id = body.get("client_id")
    context_type = body.get("context_type")
    data = body.get("data")

    if not client_id or not context_type or data is None:
        return jsonify({
            "success": False,
            "error": "client_id, context_type, and data are required"
        }), 400

    context_id = str(uuid.uuid4())
    entry = {
        "context_id": context_id,
        "client_id": client_id,
        "context_type": context_type,
        "data": data,
        "tags": body.get("tags", []),
        "aws_region": body.get("aws_region", "us-east-1"),
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    _context_store[context_id] = entry

    return jsonify({
        "success": True,
        "context_id": context_id,
        "message": "Context uploaded successfully",
        "entry": entry
    }), 201


# ---------------------------------------------------------------------------
# GET /api/v1/context/list
# ---------------------------------------------------------------------------
@context_bp.route("/list", methods=["GET"])
def list_context():
    """
    List all context entries.
    Optional query params: ?client_id=xxx  ?type=product_catalog
    """
    client_id_filter = request.args.get("client_id")
    type_filter = request.args.get("type")

    results = list(_context_store.values())

    if client_id_filter:
        results = [r for r in results if r["client_id"] == client_id_filter]
    if type_filter:
        results = [r for r in results if r["context_type"] == type_filter]

    return jsonify({
        "success": True,
        "count": len(results),
        "context_entries": results
    }), 200


# ---------------------------------------------------------------------------
# GET /api/v1/context/<context_id>
# ---------------------------------------------------------------------------
@context_bp.route("/<context_id>", methods=["GET"])
def get_context(context_id):
    """Retrieve a single context entry by ID."""
    entry = _context_store.get(context_id)
    if not entry:
        return jsonify({"success": False, "error": "Context not found"}), 404

    return jsonify({"success": True, "entry": entry}), 200


# ---------------------------------------------------------------------------
# DELETE /api/v1/context/<context_id>
# ---------------------------------------------------------------------------
@context_bp.route("/<context_id>", methods=["DELETE"])
def delete_context(context_id):
    """Delete a context entry by ID."""
    entry = _context_store.pop(context_id, None)
    if not entry:
        return jsonify({"success": False, "error": "Context not found"}), 404

    return jsonify({
        "success": True,
        "message": f"Context {context_id} deleted",
        "deleted_entry": entry
    }), 200
