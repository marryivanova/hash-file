import pytest
from flask import Flask
from flask_jwt_extended import JWTManager


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    jwt = JWTManager(app)
    return app


@pytest.fixture
def client(app):
    return app.test_client()
