from flask import Flask

from .api import api_bp


def register_routes(app: Flask):
    app.register_blueprint(api_bp, url_prefix=app.config["API_PREFIX"])
