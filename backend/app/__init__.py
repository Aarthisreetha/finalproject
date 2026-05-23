from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import register_routes
from .utils.db import init_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    init_db(app)
    register_routes(app)

    return app
