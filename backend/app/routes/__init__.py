from flask import Flask

from .api import api_bp


def register_routes(app: Flask):
    primary_prefix = app.config["API_PREFIX"].rstrip("/") or "/"
    app.register_blueprint(api_bp, url_prefix=primary_prefix)

    # Backward-compatible alias so clients using /api/* continue to work
    # when API_PREFIX is versioned (e.g. /api/v1).
    if primary_prefix.startswith("/api/"):
        app.register_blueprint(api_bp, url_prefix="/api")
