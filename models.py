from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum 
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base 
import enum

class Role(enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    role = Column(SQLEnum(Role), default=Role.OPERATOR)  


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