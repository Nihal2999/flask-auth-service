from flask import Flask
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from .models.user import db
from .config import config
from .routes.oauth import init_oauth
import redis

migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])

def create_app(config_name="default"):
    app = Flask(__name__)

    # Load config
    app.config.from_object(config[config_name])

    # Configure Redis session
    app.config["SESSION_REDIS"] = redis.from_url(app.config["REDIS_URL"])
    app.config["AUTHLIB_INSECURE_TRANSPORT"] = "true"

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    Session(app)
    init_oauth(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.token import token_bp
    from .routes.oauth import oauth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(token_bp, url_prefix="/auth")
    app.register_blueprint(oauth_bp, url_prefix="/auth")

    # Register error handlers
    from .middleware.rate_limit import register_error_handlers
    register_error_handlers(app)

    # Health check route
    @app.route("/health")
    def health():
        return {"status": "ok", "message": "Flask Auth Service is running"}, 200

    return app