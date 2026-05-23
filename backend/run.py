from app import create_app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        from app.utils.db import init_db
        from flask import g
        from pymongo import MongoClient
        client = MongoClient(app.config["MONGO_URI"])
        g.mongo_client = client
        g.db = client[app.config["MONGO_DB_NAME"]]
        from app.services.seed_service import ensure_indexes
        ensure_indexes()
    app.run(host="0.0.0.0", port=5000)
