from flask import jsonify
from .. import limiter


def register_error_handlers(app):
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({
            "error": "Too many requests",
            "message": str(e.description),
            "retry_after": e.retry_after if hasattr(e, "retry_after") else 60
        }), 429


# Rate limit decorators to reuse across routes
default_limit = "100 per minute"
auth_limit = "10 per minute"       # strict for login/register
password_limit = "5 per minute"    # very strict for password reset
token_limit = "30 per minute"      # moderate for token refresh