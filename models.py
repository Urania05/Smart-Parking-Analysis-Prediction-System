from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base # Noktasız import (Aynı klasörde oldukları için)

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String, unique=True, index=True) # e.g., A1, B4
    is_occupied = Column(Boolean, default=False)          # False: Empty, True: Occupied
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationship
    logs = relationship("ParkingLog", back_populates="parking_spot")

class ParkingLog(Base):
    __tablename__ = "parking_logs"

    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String, ForeignKey("parking_spots.spot_number"))
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)           
    vehicle_class = Column(String)                        

    # Relationship
    parking_spot = relationship("ParkingSpot", back_populates="logs")