import bcrypt
from datetime import datetime, timedelta
from .token_service import generate_access_token, generate_refresh_token
from ..models.user import db, User, PasswordReset
import secrets


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def register_user(username, email, password):
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"

    if User.query.filter_by(username=username).first():
        return None, "Username already taken"

    # Create new user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role="user",
        is_active=True,
        is_verified=False
    )

    db.session.add(user)
    db.session.commit()

    # Generate tokens
    access_token = generate_access_token(user.id, user.email, user.role)
    refresh_token = generate_refresh_token(user.id, user.email, user.role)

    return {
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }, None


def login_user(email, password):
    user = User.query.filter_by(email=email).first()

    if not user:
        return None, "Invalid email or password"

    if not user.is_active:
        return None, "Account is deactivated"

    if not user.password_hash:
        return None, "Please login with Google OAuth"

    if not verify_password(password, user.password_hash):
        return None, "Invalid email or password"

    # Generate tokens
    access_token = generate_access_token(user.id, user.email, user.role)
    refresh_token = generate_refresh_token(user.id, user.email, user.role)

    return {
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }, None


def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    return user, None


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    if "username" in data:
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != user_id:
            return None, "Username already taken"
        user.username = data["username"]

    if "password" in data:
        user.password_hash = hash_password(data["password"])

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return user, None


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"

    db.session.delete(user)
    db.session.commit()
    return True, None


def create_password_reset_token(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, "No account found with that email"

    # Generate secure token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False
    )

    db.session.add(reset)
    db.session.commit()

    return token, None


def reset_password(token, new_password):
    reset = PasswordReset.query.filter_by(token=token, used=False).first()

    if not reset:
        return False, "Invalid or expired reset token"

    if datetime.utcnow() > reset.expires_at:
        return False, "Reset token has expired"

    user = User.query.get(reset.user_id)
    if not user:
        return False, "User not found"

    user.password_hash = hash_password(new_password)
    reset.used = True
    db.session.commit()

    return True, None