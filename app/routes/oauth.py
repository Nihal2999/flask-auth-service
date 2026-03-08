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
        client_kwargs={
            "scope": "openid email profile",
            "code_challenge_method": None
        }
    )


@oauth_bp.route("/google", methods=["GET"])
def google_login():
    redirect_uri = "https://flask-auth-service-production.up.railway.app/auth/google/callback"
    return oauth.google.authorize_redirect(
        redirect_uri,
        _external=True,
        nonce=None
    )


@oauth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    try:
        from flask import session
        session.pop('_state_google_' + request.args.get('state', ''), None)
        
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info:
            return jsonify({"error": "Failed to get user info from Google"}), 400

        email = user_info["email"]
        name = user_info.get("name", email.split("@")[0])
        provider_id = user_info["sub"]

        oauth_account = OAuthAccount.query.filter_by(
            provider="google",
            provider_id=provider_id
        ).first()

        if oauth_account:
            user = oauth_account.user
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username=name.replace(" ", "_").lower(),
                    email=email,
                    password_hash=None,
                    role="user",
                    is_active=True,
                    is_verified=True
                )
                db.session.add(user)
                db.session.flush()

            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_id=provider_id
            )
            db.session.add(oauth_account)
            db.session.commit()

        access_token = generate_access_token(user.id, user.email, user.role)
        refresh_token = generate_refresh_token(user.id, user.email, user.role)

        return jsonify({
            "message": "Google login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"OAuth failed: {str(e)}"}), 400