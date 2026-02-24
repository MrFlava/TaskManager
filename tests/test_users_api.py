from types import SimpleNamespace
from unittest.mock import Mock

import pytest


class FakeQuery:
    def __init__(self, *, all_result=None, first_result=None, get_result=None, filter_first_result=None):
        self._all_result = all_result or []
        self._first_result = first_result
        self._get_result = get_result
        self._filter_first_result = filter_first_result

    def all(self):
        return self._all_result

    def filter_by(self, **kwargs):
        return FakeQuery(first_result=self._filter_first_result)

    def filter(self, *args, **kwargs):
        return FakeQuery(first_result=self._filter_first_result)

    def first(self):
        return self._first_result

    def get_or_404(self, _id):
        if self._get_result is None:
            raise Exception("404")
        return self._get_result


def make_user_dict(user_id=1, name="John", email="john@example.com", created_at=None):
    return {"id": user_id, "name": name, "email": email, "created_at": created_at}


def test_create_user_duplicate_email_returns_400(client, monkeypatch):
    from app.api import users as users_module

    existing = SimpleNamespace(to_dict=lambda: make_user_dict())
    monkeypatch.setattr(users_module.User, "query", FakeQuery(filter_first_result=existing))

    resp = client.post(
        "/api/users/",
        json={"name": "John", "email": "john@example.com", "password": "x"},
    )

    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Email already exists"


def test_create_user_invalid_email_returns_422(client):
    resp = client.post(
        "/api/users/",
        json={"name": "John", "email": "not-an-email", "password": "x"},
    )

    assert resp.status_code == 422
    body = resp.get_json()
    assert body["status"] == "error"
    assert "details" in body


def test_patch_user_partial_update_success(client, monkeypatch):
    from app.api import users as users_module

    user_obj = SimpleNamespace(
        id=1,
        name="John",
        email="john@example.com",
        password="pass",
        to_dict=lambda: make_user_dict(name="John Updated"),
    )

    monkeypatch.setattr(users_module.User, "query", FakeQuery(get_result=user_obj, filter_first_result=None))

    session = Mock()
    monkeypatch.setattr(users_module.db, "session", session)

    resp = client.patch("/api/users/1/", json={"name": "John Updated"})

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["user"]["name"] == "John Updated"
    session.commit.assert_called_once()


def test_delete_user_requires_correct_password(client, monkeypatch):
    from app.api import users as users_module

    user_obj = SimpleNamespace(
        id=1,
        name="John",
        email="john@example.com",
        password="secret",
        to_dict=lambda: make_user_dict(),
    )
    monkeypatch.setattr(users_module.User, "query", FakeQuery(get_result=user_obj))

    session = Mock()
    monkeypatch.setattr(users_module.db, "session", session)

    resp = client.delete("/api/users/1/", json={"password": "wrong"})

    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Incorrect password"
    session.delete.assert_not_called()


def test_get_user_by_id_returns_schema(client, monkeypatch):
    from app.api import users as users_module

    user_obj = SimpleNamespace(to_dict=lambda: make_user_dict())
    monkeypatch.setattr(users_module.User, "query", FakeQuery(get_result=user_obj))

    resp = client.get("/api/users/1/")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["user"]["email"] == "john@example.com"
