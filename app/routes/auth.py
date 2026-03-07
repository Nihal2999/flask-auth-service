from flask import Blueprint, request, jsonify
from .. import limiter
from ..services.token_service import blacklist_token
from ..utils.decorators import token_required
from ..middleware.rate_limit import auth_limit, password_limit
from ..services.auth_service import (
    register_user, login_user, create_password_reset_token, reset_password
)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit(auth_limit)
def register():
    data = request.get_json()

    # Validate required fields
    required = ["username", "email", "password"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Validate password length
    if len(data["password"]) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    result, error = register_user(
        username=data["username"],
        email=data["email"],
        password=data["password"]
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User registered successfully",
        "user": result["user"],
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"]
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit(auth_limit)
def login():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    result, error = login_user(
        email=data["email"],
        password=data["password"]
    )

    if error:
        return jsonify({"error": error}), 401

    return jsonify({
        "message": "Login successful",
        "user": result["user"],
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"]
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    success = blacklist_token(token)
    if not success:
        return jsonify({"error": "Logout failed"}), 400

    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me():
    from ..models.user import User
    user = User.query.get(request.current_user["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_me():
    from ..services.auth_service import update_user
    data = request.get_json()
    user, error = update_user(request.current_user["user_id"], data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["DELETE"])
@token_required
def delete_me():
    from ..services.auth_service import delete_user
    success, error = delete_user(request.current_user["user_id"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Account deleted successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit(password_limit)
def forgot_password():
    data = request.get_json()
    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    token, error = create_password_reset_token(data["email"])
    if error:
        return jsonify({"error": error}), 400

    # In production this token would be emailed
    # For now return it directly for testing
    return jsonify({
        "message": "Password reset token generated",
        "reset_token": token
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json()

    if not data.get("token") or not data.get("new_password"):
        return jsonify({"error": "Token and new_password are required"}), 400

    if len(data["new_password"]) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    success, error = reset_password(data["token"], data["new_password"])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Password reset successfully"}), 200