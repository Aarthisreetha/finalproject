import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _Config(dict):
    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


class _JsonResponse:
    def __init__(self, payload):
        self.json = payload




class _G(dict):
    __getattr__ = dict.get

    def __setattr__(self, key, value):
        self[key] = value


class _Blueprint:
    def __init__(self, _name, _import_name):
        self.routes = {}

    def _register(self, path, fn):
        self.routes[path] = fn
        return fn

    def get(self, path):
        return lambda fn: self._register(path, fn)

    def post(self, path):
        return lambda fn: self._register(path, fn)

    def patch(self, path):
        return lambda fn: self._register(path, fn)


class _Flask:
    def __init__(self, _name):
        self.config = _Config()
        self._before = []
        self._teardown = []
        self._routes = {}

    def before_request(self, fn):
        self._before.append(fn)
        return fn

    def teardown_request(self, fn):
        self._teardown.append(fn)
        return fn

    def register_blueprint(self, bp, url_prefix=""):
        for path, fn in bp.routes.items():
            self._routes[f"{url_prefix}{path}"] = fn

    def test_client(self):
        app = self

        class _Client:
            def get(self, path):
                flask_mod.current_app = app
                from app.utils import db as _db_mod
                _db_mod.current_app = app
                _db_mod.g = flask_mod.g = _G()
                for fn in app._before:
                    fn()
                try:
                    result = app._routes[path]()
                finally:
                    for fn in app._teardown:
                        fn(None)
                if isinstance(result, tuple):
                    body, status = result
                else:
                    body, status = result, 200
                resp = _JsonResponse(body.json if isinstance(body, _JsonResponse) else body)
                resp.status_code = status
                return resp

        return _Client()


flask_mod = ModuleType("flask")
flask_mod.Flask = _Flask
flask_mod.Blueprint = _Blueprint
flask_mod.current_app = None
flask_mod.g = _G()
flask_mod.request = SimpleNamespace(get_json=lambda force=True: {})
flask_mod.jsonify = lambda payload: _JsonResponse(payload)
sys.modules.setdefault("flask", flask_mod)

cors_mod = ModuleType("flask_cors")
cors_mod.CORS = lambda _app: None
sys.modules.setdefault("flask_cors", cors_mod)

bson_mod = ModuleType("bson")
bson_mod.ObjectId = lambda value: value
sys.modules.setdefault("bson", bson_mod)

bson_errors_mod = ModuleType("bson.errors")


class InvalidId(Exception):
    pass


bson_errors_mod.InvalidId = InvalidId
sys.modules.setdefault("bson.errors", bson_errors_mod)

pymongo_mod = ModuleType("pymongo")
pymongo_mod.MongoClient = object
sys.modules.setdefault("pymongo", pymongo_mod)

from app import create_app


class MockClient:
    def __getitem__(self, _item):
        return object()

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


def test_health_api_alias(monkeypatch):
    from app.utils import db as db_mod

    monkeypatch.setattr(db_mod, "MongoClient", lambda *_args, **_kwargs: MockClient())

    app = create_app()
    client = app.test_client()

    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json["status"] == "ok"
