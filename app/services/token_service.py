import jwt
import redis
import uuid
from datetime import datetime, timedelta
from flask import current_app

redis_client = None

def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(current_app.config["REDIS_URL"])
    return redis_client


def generate_access_token(user_id, email, role):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),  # unique token ID
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(
            minutes=current_app.config["ACCESS_TOKEN_EXPIRE_MINUTES"]
        )
    }
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )
    return token


def generate_refresh_token(user_id, email, role):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(
            days=current_app.config["REFRESH_TOKEN_EXPIRE_DAYS"]
        )
    }
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )
    return token


def decode_token(token):
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def blacklist_token(token):
    try:
        r = get_redis()
        payload, error = decode_token(token)
        if error:
            return False
        # Store in Redis until token expiry
        exp = payload["exp"]
        now = datetime.utcnow().timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            r.setex(f"blacklist:{token}", ttl, "true")
        return True
    except Exception:
        return False


def is_token_blacklisted(token):
    try:
        r = get_redis()
        return r.exists(f"blacklist:{token}") == 1
    except Exception:
        return False