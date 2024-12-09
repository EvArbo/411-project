import pytest
from fitness_tracker_app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_success(client):
    response = client.post('/login', json={"username": "test", "password": "password"})
    assert response.status_code == 200
    assert response.json == {"message": "Login successful."}