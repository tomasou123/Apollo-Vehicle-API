from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from typing import Annotated, List
import random
import string

from database import Base, engine, get_db
import models
from schemas import VehicleCreate, VehicleResponse, VehicleUpdate

"""Helper methods to create new VIN numbers for the vehicles"""
def _generate_vin():
    characters = string.digits + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choices(population=characters, k=17))

def _get_unique_vin(db: Session):
    #check that the gnerate one is unique i.e. not in the databse --> not likely to be repeated
    while True:
        new_vin = _generate_vin()
        result = db.execute(
            select(models.Vehicle).where(models.Vehicle.vin == new_vin),
        )

        existing_vehicle = result.scalars().first()

        if not existing_vehicle:
            return new_vin


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Database")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    #check for json invalid error, then 
    for error in exc.errors():
        if error.get("type") == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Bad Request: Unable to parse the request body as JSON."}
            )
            
    #if json is good but failed validation for json then 422
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.get("/vehicle", response_model=List[VehicleResponse], status_code=status.HTTP_200_OK)
def get_vehicles(db: Annotated[Session, Depends(get_db)]):
    """
    Gets all vehicles currently stored in the database.
    
    Parameters:
    - db: database we access
    
    Returns:
    - List[Vehicle]: A list of all vehicle records (JSON formatted).
    """
    #query all the vehicles in the db
    result = db.execute(
        select(models.Vehicle),   
    )

    #get vehicle instances
    vehicles = result.scalars().all()

    return vehicles

@app.post("/vehicle", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Creates a new vehicle record and assigns it a unique identifier.
    
    Parameters:
    - vehicle: The vehicle information
    - db: database we access
    
    Returns:
    - Vehicle: The newly created vehicle object, including its generated unique identifier.
    """
    #generate a new VIN number that is unique --> then add to db and commit

    unique_vin = _get_unique_vin(db)

    #make new vehicle with the info provided and the vin created
    new_vehicle = models.Vehicle(
        vin=unique_vin,
        **vehicle.model_dump() #turns to dict
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle

@app.get("/vehicle/{vin}", response_model=VehicleResponse)
def get_vehicle(vin: str, db: Annotated[Session, Depends(get_db)]):
    """
    Retrieves a specific vehicle's information based on its unique identifier.
    
    Parameters:
    - vin (str): unique vin number
    - db : database we access
    
    Returns:
    - Vehicle: The vehicle object containing its information if found.
    - Raises 404 HTTPException: If the vehicle does not exist in the database.
    """
    search_vin = vin.upper() #for case insensitivity

    #query for this specific vin number vehicle
    results = db.execute(
        select(models.Vehicle).where(models.Vehicle.vin == search_vin),
    )
    #check if results is empty
    vehicle = results.scalars().first()
    if vehicle:
        return vehicle

    raise HTTPException(status_code=404, detail="Unable to find vehicle.")
    
    

@app.put("/vehicle/{vin}", response_model=VehicleResponse)
def update_vehicle(vin: str, new_info: VehicleUpdate, db: Annotated[Session, Depends(get_db)]):
    """
    Updates the information of an existing vehicle in the database.
    
    Parameters:
    - vin (str): unique vin number
    - new_info: the new data to overwrite the existing vehicles attributes.
    
    Returns:
    - Vehicle: The fully updated vehicle object.
    - Raises 404 HTTPException: If the vehicle does not exist.
    """
    search_vin = vin.upper()
    #get the current vehicle --> check if it exsits, then want to replace the given information with that vin vehicle with new information

    #get the vin that matches
    results = db.execute(
        select(models.Vehicle).where(models.Vehicle.vin == search_vin),
    )

    vehicle = results.scalars().first()

    #check that it exists
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unable to find vehicle.")
    
    #exists, now make the change
    new_data = new_info.model_dump(exclude_unset=True) #turns to dict and ignores Nones
    
    for key, value in new_data.items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@app.delete("/vehicle/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def remove_vehicle(vin: str, db: Annotated[Session, Depends(get_db)]):
    """
    Deletes a specific vehicle from the database.
    
    Parameters:
    - vin (str): unique vin number
    
    Returns:
    - 204 Status code
    - Raises 404 HTTPException: If the vehicle does not exist.
    """
    search_vin = vin.upper()
    #query then check if exist, then remove from the db
    results = db.execute(
        select(models.Vehicle).where(models.Vehicle.vin == search_vin),
    )

    vehicle = results.scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unable to find vehicle.")

    #if it does exist, then delte from db
    db.delete(vehicle)
    db.commit()

