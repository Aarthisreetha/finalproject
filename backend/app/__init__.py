from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import register_routes
from .services.seed_service import ensure_indexes
from .utils.db import init_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    init_db(app)
    ensure_indexes()
    register_routes(app)

    return app
