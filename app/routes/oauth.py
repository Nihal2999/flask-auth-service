from flask import Blueprint, request, jsonify, redirect, current_app
from authlib.integrations.flask_client import OAuth
from ..models.user import db, User, OAuthAccount
from ..services.token_service import generate_access_token, generate_refresh_token
import os

oauth_bp = Blueprint("oauth", __name__)
oauth = OAuth()


def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"}
    )


@oauth_bp.route("/google", methods=["GET"])
def google_login():
    redirect_uri = "http://localhost:5000/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri)


@oauth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info:
            return jsonify({"error": "Failed to get user info from Google"}), 400

        email = user_info["email"]
        name = user_info.get("name", email.split("@")[0])
        provider_id = user_info["sub"]

        # Check if OAuth account exists
        oauth_account = OAuthAccount.query.filter_by(
            provider="google",
            provider_id=provider_id
        ).first()

        if oauth_account:
            # Existing OAuth user — just login
            user = oauth_account.user
        else:
            # Check if email already registered normally
            user = User.query.filter_by(email=email).first()

            if not user:
                # Create new user
                user = User(
                    username=name.replace(" ", "_").lower(),
                    email=email,
                    password_hash=None,
                    role="user",
                    is_active=True,
                    is_verified=True  # Google already verified the email
                )
                db.session.add(user)
                db.session.flush()

            # Link OAuth account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_id=provider_id
            )
            db.session.add(oauth_account)
            db.session.commit()

        # Generate tokens
        access_token = generate_access_token(user.id, user.email, user.role)
        refresh_token = generate_refresh_token(user.id, user.email, user.role)

        return jsonify({
            "message": "Google login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        return jsonify({"error": f"OAuth failed: {str(e)}"}), 400