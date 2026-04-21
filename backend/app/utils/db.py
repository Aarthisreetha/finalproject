from flask import current_app, g
from pymongo import MongoClient


def init_db(app):
    @app.before_request
    def _set_db():
        if "mongo_client" not in g:
            client = MongoClient(current_app.config["MONGO_URI"])
            g.mongo_client = client
            g.db = client[current_app.config["MONGO_DB_NAME"]]

    @app.teardown_request
    def _close_db(exception):
        client = g.pop("mongo_client", None)
        g.pop("db", None)
        if client:
            client.close()


def get_db():
    return g.db
