from types import SimpleNamespace


class FakeQuery:
    def __init__(self, *, first_result=None, get_result=None, filter_items=None, count_value=0):
        self._first_result = first_result
        self._get_result = get_result
        self._filter_items = filter_items or []
        self._count_value = count_value

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self._first_result

    def get_or_404(self, _id):
        if self._get_result is None:
            raise Exception("404")
        return self._get_result

    def order_by(self, *args, **kwargs):
        return self

    def count(self):
        return self._count_value

    def offset(self, _):
        return self

    def limit(self, _):
        return self

    def all(self):
        return self._filter_items


def test_tasks_by_project_requires_email_422(client):
    resp = client.get("/api/tasks/project/1/")
    assert resp.status_code == 422


def test_tasks_by_project_forbidden_when_user_not_in_project(client, monkeypatch):
    from app.api import tasks as tasks_module

    user_obj = SimpleNamespace(email="john@example.com")
    project_obj = SimpleNamespace(users=[])

    monkeypatch.setattr(tasks_module.User, "query", FakeQuery(first_result=user_obj))
    monkeypatch.setattr(tasks_module.Project, "query", FakeQuery(get_result=project_obj))

    resp = client.get("/api/tasks/project/1/?email=john@example.com")
    assert resp.status_code == 403


def test_tasks_by_project_paginates(client, monkeypatch):
    from app.api import tasks as tasks_module

    user_obj = SimpleNamespace(email="john@example.com")
    project_obj = SimpleNamespace(users=[user_obj])

    task1 = SimpleNamespace(to_dict=lambda: {"id": 1, "title": "T1", "description": None, "order": 1, "project_id": 1, "created_at": None, "updated_at": None})
    task2 = SimpleNamespace(to_dict=lambda: {"id": 2, "title": "T2", "description": None, "order": 2, "project_id": 1, "created_at": None, "updated_at": None})

    monkeypatch.setattr(tasks_module.User, "query", FakeQuery(first_result=user_obj))
    monkeypatch.setattr(tasks_module.Project, "query", FakeQuery(get_result=project_obj))

    # patch Task.query chain
    monkeypatch.setattr(tasks_module.Task, "query", FakeQuery(filter_items=[task1, task2], count_value=2))

    resp = client.get("/api/tasks/project/1/?email=john@example.com&page=1&per_page=1")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["pagination"]["total"] == 2
    assert body["pagination"]["per_page"] == 1
    assert isinstance(body["tasks"], list)
