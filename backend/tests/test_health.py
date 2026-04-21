import mongomock
from app import create_app


class MockClient:
    def __init__(self):
        self._client = mongomock.MongoClient()

    def __getitem__(self, item):
        return self._client[item]

    def close(self):
        return None


def test_health(monkeypatch):
    from app.utils import db as db_mod

    monkeypatch.setattr(db_mod, "MongoClient", lambda *_args, **_kwargs: MockClient())

    app = create_app()
    client = app.test_client()

    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json["status"] == "ok"
