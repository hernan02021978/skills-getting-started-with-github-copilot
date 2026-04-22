import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Estado inicial de activities para resetear en cada test
initial_activities = copy.deepcopy(activities)

@pytest.fixture
def client():
    # Resetea el estado de activities antes de cada test
    global activities
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    return TestClient(app)

# Pruebas para GET /activities
def test_get_activities_success(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

# Pruebas para POST /activities/{activity_name}/signup
def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    # Verifica que se agregó al diccionario
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_email_already_signed_up(client):
    # Primero, inscríbete
    client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    # Intenta inscribirte de nuevo
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]

# Pruebas para DELETE /activities/{activity_name}/signup
def test_remove_signup_success(client):
    # Primero, inscríbete
    client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    # Luego, remueve
    response = client.delete("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    # Verifica que se removió
    assert "test@mergington.edu" not in activities["Chess Club"]["participants"]

def test_remove_signup_activity_not_found(client):
    response = client.delete("/activities/NonExistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_remove_signup_not_signed_up(client):
    response = client.delete("/activities/Chess Club/signup?email=notsigned@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" in data["detail"]