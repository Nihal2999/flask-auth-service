from functools import wraps
from flask import request, jsonify
from ..services.token_service import decode_token, is_token_blacklisted


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Access token is missing"}), 401

        # Check if token is blacklisted
        if is_token_blacklisted(token):
            return jsonify({"error": "Token has been revoked"}), 401

        # Decode token
        payload, error = decode_token(token)
        if error:
            return jsonify({"error": error}), 401

        # Check token type
        if payload.get("type") != "access":
            return jsonify({"error": "Invalid token type"}), 401

        # Attach user info to request
        request.current_user = {
            "user_id": payload["user_id"],
            "email": payload["email"],
            "role": payload["role"]
        }

        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # token_required must be applied first
            if not hasattr(request, "current_user"):
                return jsonify({"error": "Authentication required"}), 401

            user_role = request.current_user.get("role")
            if user_role not in roles:
                return jsonify({
                    "error": f"Access denied. Required roles: {list(roles)}"
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, "current_user"):
            return jsonify({"error": "Authentication required"}), 401

        if request.current_user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)
    return decorated