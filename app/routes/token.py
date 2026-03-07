from flask import Blueprint, request, jsonify
from ..services.token_service import (
    decode_token, generate_access_token,
    generate_refresh_token, blacklist_token, is_token_blacklisted
)
from ..models.user import User

token_bp = Blueprint("token", __name__)


@token_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    data = request.get_json()

    if not data.get("refresh_token"):
        return jsonify({"error": "Refresh token is required"}), 400

    refresh_token = data["refresh_token"]

    # Check if blacklisted
    if is_token_blacklisted(refresh_token):
        return jsonify({"error": "Refresh token has been revoked"}), 401

    # Decode refresh token
    payload, error = decode_token(refresh_token)
    if error:
        return jsonify({"error": error}), 401

    # Validate token type
    if payload.get("type") != "refresh":
        return jsonify({"error": "Invalid token type"}), 401

    # Get user from DB
    user = User.query.get(payload["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 401

    # Blacklist old refresh token
    blacklist_token(refresh_token)

    # Generate new tokens
    new_access_token = generate_access_token(user.id, user.email, user.role)
    new_refresh_token = generate_refresh_token(user.id, user.email, user.role)

    return jsonify({
        "message": "Tokens refreshed successfully",
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }), 200


@token_bp.route("/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json()

    if not data.get("token"):
        return jsonify({"error": "Token is required"}), 400

    token = data["token"]

    # Check if blacklisted
    if is_token_blacklisted(token):
        return jsonify({"valid": False, "error": "Token has been revoked"}), 401

    # Decode token
    payload, error = decode_token(token)
    if error:
        return jsonify({"valid": False, "error": error}), 401

    return jsonify({
        "valid": True,
        "user_id": payload["user_id"],
        "email": payload["email"],
        "role": payload["role"],
        "type": payload["type"],
        "expires_at": payload["exp"]
    }), 200