import sys
from pathlib import Path

import pytest
from flask import Flask


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def app():
    from main import create_app

    app = create_app()
    app.config.update(TESTING=True)

    ctx = app.app_context()
    ctx.push()
    try:
        yield app
    finally:
        ctx.pop()


@pytest.fixture()
def client(app):
    return app.test_client()
