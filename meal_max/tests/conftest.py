import pytest
import os

from app import create_app
from config import TestConfig
from dotenv import load_dotenv
from meal_max.db import db

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

load_dotenv()

@pytest.fixture
def wger_api_key():
    key = os.getenv("WGER_API_KEY")
    if not key:
        raise ValueError("WGER_API_KEY not found in environment variables")
    return key
