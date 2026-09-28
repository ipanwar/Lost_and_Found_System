import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from database import get_session
from main import app
from models import ItemStatus


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_item_success(client: TestClient):
    payload = {
        "title": "Blue Dell Laptop",
        "description": "Dell Inspiron with sticker on cover, left at Library 2nd floor",
        "category": "Electronics",
        "location": "Central Library Floor 2",
        "reported_by": "Alex Johnson",
        "status": "Lost"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Blue Dell Laptop"
    assert data["description"] == payload["description"]
    assert data["category"] == "Electronics"
    assert data["location"] == "Central Library Floor 2"
    assert data["reported_by"] == "Alex Johnson"
    assert data["status"] == "Lost"


def test_create_item_validation_empty_title(client: TestClient):
    payload = {
        "title": "   ",
        "description": "Found a blue notebook",
        "category": "Stationery",
        "location": "Room 101",
        "reported_by": "Sam",
        "status": "Found"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


def test_create_item_validation_invalid_status(client: TestClient):
    payload = {
        "title": "Calculator",
        "description": "Casio FX-991EX",
        "category": "Electronics",
        "location": "Math Lab",
        "reported_by": "Alice",
        "status": "Missing"  # Invalid status
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


def test_get_all_items(client: TestClient):
    # Seed 2 items
    client.post("/items", json={
        "title": "Student ID Card",
        "description": "ID card belonging to CS department",
        "category": "Documents",
        "location": "Cafeteria",
        "reported_by": "Sarah",
        "status": "Found"
    })
    client.post("/items", json={
        "title": "Titan Watch",
        "description": "Silver metallic wrist watch",
        "category": "Accessories",
        "location": "Gymnasium",
        "reported_by": "Michael",
        "status": "Lost"
    })

    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_item_by_id_found(client: TestClient):
    res = client.post("/items", json={
        "title": "Calculus Textbook",
        "description": "Stewart Calculus 8th Edition",
        "category": "Books",
        "location": "Room 304",
        "reported_by": "Emily",
        "status": "Found"
    })
    item_id = res.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Calculus Textbook"


def test_get_item_by_id_not_found(client: TestClient):
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_update_item(client: TestClient):
    res = client.post("/items", json={
        "title": "House Keys",
        "description": "Bunch of 3 keys with a red keychain",
        "category": "Accessories",
        "location": "Parking Lot",
        "reported_by": "David",
        "status": "Lost"
    })
    item_id = res.json()["id"]

    # Update status to Returned and location
    update_payload = {
        "status": "Returned",
        "location": "Security Office Desk"
    }
    response = client.put(f"/items/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Returned"
    assert data["location"] == "Security Office Desk"
    assert data["title"] == "House Keys"  # unchanged


def test_update_item_not_found(client: TestClient):
    response = client.put("/items/9999", json={"status": "Found"})
    assert response.status_code == 404


def test_delete_item(client: TestClient):
    res = client.post("/items", json={
        "title": "Water Bottle",
        "description": "Black Milton 1L bottle",
        "category": "Accessories",
        "location": "Auditorium",
        "reported_by": "Rachel",
        "status": "Found"
    })
    item_id = res.json()["id"]

    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == item_id

    # Confirm it cannot be retrieved
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 404


def test_delete_item_not_found(client: TestClient):
    response = client.delete("/items/9999")
    assert response.status_code == 404


def test_filter_items_by_status(client: TestClient):
    client.post("/items", json={
        "title": "Item 1",
        "description": "Desc 1",
        "category": "Electronics",
        "location": "Lab 1",
        "reported_by": "User 1",
        "status": "Lost"
    })
    client.post("/items", json={
        "title": "Item 2",
        "description": "Desc 2",
        "category": "Electronics",
        "location": "Lab 2",
        "reported_by": "User 2",
        "status": "Found"
    })
    client.post("/items", json={
        "title": "Item 3",
        "description": "Desc 3",
        "category": "Electronics",
        "location": "Lab 3",
        "reported_by": "User 3",
        "status": "Lost"
    })

    lost_res = client.get("/items/status/Lost")
    assert lost_res.status_code == 200
    assert len(lost_res.json()) == 2

    found_res = client.get("/items/status/Found")
    assert found_res.status_code == 200
    assert len(found_res.json()) == 1


def test_filter_items_by_category(client: TestClient):
    client.post("/items", json={
        "title": "Laptop",
        "description": "MacBook Pro",
        "category": "Electronics",
        "location": "Library",
        "reported_by": "Anna",
        "status": "Lost"
    })
    client.post("/items", json={
        "title": "Passport",
        "description": "Indian Passport in brown cover",
        "category": "Documents",
        "location": "Admin Block",
        "reported_by": "Brian",
        "status": "Found"
    })

    cat_res = client.get("/items/category/electronics")
    assert cat_res.status_code == 200
    items = cat_res.json()
    assert len(items) == 1
    assert items[0]["title"] == "Laptop"
