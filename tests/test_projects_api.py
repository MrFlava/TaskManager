from types import SimpleNamespace
from unittest.mock import Mock


class FakeQuery:
    def __init__(self, *, all_result=None, get_result=None, first_result=None):
        self._all_result = all_result or []
        self._get_result = get_result
        self._first_result = first_result

    def all(self):
        return self._all_result

    def get_or_404(self, _id):
        if self._get_result is None:
            raise Exception("404")
        return self._get_result

    def filter_by(self, **kwargs):
        return FakeQuery(first_result=self._first_result)

    def first(self):
        return self._first_result


def test_add_user_to_project_validates_email_422(client):
    resp = client.post("/api/projects/1/users/", json={"email": "bad"})
    assert resp.status_code == 422


def test_add_user_to_project_enforces_max_3_users(client, monkeypatch):
    from app.api import projects as projects_module

    # project.add_user raises ValueError when full
    project_obj = SimpleNamespace(
        users=[1, 2, 3],
        title="P1",
        to_dict=lambda: {"id": 1, "title": "P1", "description": None, "order": 0, "created_at": None, "updated_at": None, "user_count": 3},
        add_user=lambda _u: (_ for _ in ()).throw(ValueError("Project P1 already has maximum 3 users")),
    )

    user_obj = SimpleNamespace(email="john@example.com")

    monkeypatch.setattr(projects_module.Project, "query", FakeQuery(get_result=project_obj))
    monkeypatch.setattr(projects_module.User, "query", FakeQuery(first_result=user_obj))

    session = Mock()
    monkeypatch.setattr(projects_module.db, "session", session)

    resp = client.post("/api/projects/1/users/", json={"email": "john@example.com"})

    assert resp.status_code == 400
    assert "maximum 3 users" in resp.get_json()["message"]
    session.commit.assert_not_called()
