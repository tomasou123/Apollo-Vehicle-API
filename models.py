from sqlalchemy import Integer, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

#vehicle object for the database
class Vehicle(Base):
    __tablename__ = "vehicles"

    # VIN is unique id and pimary id --> since we convert to uppercase in pydantic then unqiue is true
    vin: Mapped[str] = mapped_column(String(17), primary_key=True, index=True)
    
    manufacturer_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    horse_power: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_year: Mapped[int] = mapped_column(Integer, nullable=False)
    
    #allow for accurate amounts of purchases
    purchase_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False) 
    fuel_type: Mapped[str] = mapped_column(String(20), nullable=False)