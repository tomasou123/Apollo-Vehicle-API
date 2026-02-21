from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime


"""
* A vehicle is uniquely identified by the VIN (Vehicle identification number). In addition, the following additional attributes need to be considered:
* manufacturer name (string)
* description (string)
* horse power (integer)
* model name (string)
* model year (integer)
* purchase price (decimal)
* fuel type (string)
* VIN has a unique constraint (case-insensitive).
"""

#for fuels
class FuelType(str, Enum):
    gasoline = "Gasoline"
    diesel = "Diesel"
    electric = "Electric"
    hybrid = "Hybrid"

#what the user will provide
class VehicleBase(BaseModel):
    manufacturer_name: str = Field(min_length=1, max_length=50)
    description: str = Field(max_length=255, default="")
    horse_power: int = Field(gt=0) #must be positive
    model_name: str = Field(min_length=1)
    model_year: int = Field(ge=1885, le=datetime.now().year + 1) #when first car was made so must be sooner than then and less or equal to this year
    purchase_price: Decimal = Field(ge=0.0) #cant be 0
    fuel_type: FuelType

#same as Base --> no vin required
class VehicleCreate(VehicleBase):
    pass

#dont need to provide all parameters --> update base --> inhereit base model instead of vehiclebase
class VehicleUpdate(BaseModel):
    #Will keep previous values if not inputted
    manufacturer_name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    horse_power: int | None = Field(default=None, gt=0)
    model_name: str | None = Field(default=None, min_length=1)
    model_year: int | None = Field(default=None, ge=1885, le=datetime.now().year + 1)
    purchase_price: Decimal | None = Field(default=None, ge=0.0)
    fuel_type: FuelType | None = None

#add vin as requirement
class VehicleResponse(VehicleBase):
    vin: str = Field(min_length=17, max_length=17) #VIN numbers are 17 characters long --> convert to all upercase
    model_config = ConfigDict(from_attributes=True)

