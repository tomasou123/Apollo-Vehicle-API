import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your application and database components
from main import app
from database import Base, get_db

# 1. Setup an IN-MEMORY SQLite database specifically for testing
# This ensures tests are fast and don't leave junk data behind
#in mem SQL lite database for testing --> fast and dont leave information behind
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#create the tables
Base.metadata.create_all(bind=engine)

#override function
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db

#tester client
client = TestClient(app)

#help unit tests get good json
def get_valid_payload():
    return {
        "manufacturer_name": "Ford",
        "description": "A reliable test truck.",
        "horse_power": 400,
        "model_name": "F-150",
        "model_year": 2024,
        "purchase_price": 45000.00,
        "fuel_type": "Gasoline"
    }

#create test 
def test_create_vehicle():
    """Test creating a new vehicle successfully"""
    response = client.post(
        "/vehicle",
        json={
            "manufacturer_name": "Toyota",
            "description": "A reliable sedan.",
            "horse_power": 169,
            "model_name": "Camry",
            "model_year": 2023,
            "purchase_price": 26000.50,
            "fuel_type": "Gasoline"
        }
    )
    
    assert response.status_code == 201
    
    #check matched data
    data = response.json()
    assert data["manufacturer_name"] == "Toyota"
    assert data["model_name"] == "Camry"
    
    #check vin existence
    assert "vin" in data
    assert len(data["vin"]) == 17


def test_get_vehicle_not_found():
    #random vin
    response = client.get("/vehicle/FAKEVIN1234567890")

    assert response.status_code == 404
    assert response.json()["detail"] == "Unable to find vehicle."


#for missing fields --> tests them all
@pytest.mark.parametrize("missing_field", [
    "manufacturer_name", "horse_power", "model_name", "model_year", "purchase_price", "fuel_type"
])
def test_create_vehicle_missing_requirements(missing_field):
    """Test that omitting any required field results in a 422 Error"""
    payload = get_valid_payload()
    del payload[missing_field]
    
    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422
    assert missing_field in response.text

def test_create_vehicle_bad_json_400():
    #data instead of json
    response = client.post("/vehicle", content="{this_is_not_valid_json: True,}")
    
    assert response.status_code == 400
    assert "Unable to parse the request body as JSON" in response.json()["error"]

def test_create_vehicle_unprocessable_422():
    #test limits of data we want
    payload = get_valid_payload()
    payload["horse_power"] = -50
    payload["model_year"] = 1000
    
    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422


def test_create_and_get_specific_vehicle():
    payload = get_valid_payload()
    
    #create the vehicle instance
    post_response = client.post("/vehicle", json=payload)
    assert post_response.status_code == 201
    vin = post_response.json()["vin"]

    #find vehicle with vin
    get_response = client.get(f"/vehicle/{vin}")
    assert get_response.status_code == 200
    assert get_response.json()["vin"] == vin
    assert get_response.json()["manufacturer_name"] == "Ford"

def test_get_multiple_vehicles():
    #multiple vehicles 
    payload2 = get_valid_payload()
    payload2["model_name"] = "Mustang"
    client.post("/vehicle", json=payload2) #its own vin

    get_response = client.get("/vehicle")
    assert get_response.status_code == 200
    
    vehicles = get_response.json()
    assert len(vehicles) >= 2 

def test_update_vehicle_partial_data():
    #updating vehicle
    payload = get_valid_payload()
    post_response = client.post("/vehicle", json=payload)
    vin = post_response.json()["vin"]

    update_payload = {
        "purchase_price": 50000.00,
        "description": "Price increased due to demand."
    }

    put_response = client.put(f"/vehicle/{vin}", json=update_payload)
    assert put_response.status_code == 200
    
    #check the changes
    updated_vehicle = put_response.json()
    assert updated_vehicle["purchase_price"] == "50000.00"
    assert updated_vehicle["description"] == "Price increased due to demand."
    
    #check other data
    assert updated_vehicle["manufacturer_name"] == "Ford"
    assert updated_vehicle["horse_power"] == 400

def test_delete_vehicle():
    #delete vehicle
    payload = get_valid_payload()
    post_response = client.post("/vehicle", json=payload)
    vin = post_response.json()["vin"]

    delete_response = client.delete(f"/vehicle/{vin}")
    assert delete_response.status_code == 204

    #doesnt exist
    get_response = client.get(f"/vehicle/{vin}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Unable to find vehicle."

def test_case_insensitive_vin():
    payload = get_valid_payload()
    post_response = client.post("/vehicle", json=payload)
    
    original_vin = post_response.json()["vin"]
    lowercase_vin = original_vin.lower()
    
    #ask for lowercase vin
    get_response = client.get(f"/vehicle/{lowercase_vin}")
    
    assert get_response.status_code == 200
    assert get_response.json()["vin"] == original_vin


def test_update_vehicle_not_found():
    #update non existing vehicle
    update_payload = {"purchase_price": 50000.00}
    put_response = client.put("/vehicle/FAKEVIN1234567890", json=update_payload)
    
    assert put_response.status_code == 404
    assert put_response.json()["detail"] == "Unable to find vehicle."

def test_delete_vehicle_not_found():
    #delete non existing vehicle
    delete_response = client.delete("/vehicle/FAKEVIN1234567890")
    
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Unable to find vehicle."

def test_invalid_fuel_type_enum():
    #different fuel
    payload = get_valid_payload()
    payload["fuel_type"] = "Some other fuel" # Not in the FuelType Enum
    
    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422
    assert "Input should be" in response.text

def test_empty_string_validation():
    #empty strings
    payload = get_valid_payload()
    payload["manufacturer_name"] = "" # Empty string, violates min_length=1
    
    response = client.post("/vehicle", json=payload)
    assert response.status_code == 422
    assert "String should have at least 1 character" in response.text