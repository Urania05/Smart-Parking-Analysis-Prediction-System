from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import uuid

# ==========================================
# 1. ENCAPSULATION & ABSTRACTION
# ==========================================
class Vehicle(ABC):
    def __init__(self):
        self.__ticket_id = str(uuid.uuid4())[:8].upper()
        self.__entry_time = datetime.now()

    def get_ticket_id(self) -> str:
        return self.__ticket_id

    def get_entry_time(self) -> datetime:
        return self.__entry_time

    @abstractmethod
    def calculate_fee(self, exit_time: datetime) -> float:
        pass

# ==========================================
# 2. INHERITANCE & POLYMORPHISM
# ==========================================
class Car(Vehicle):
    def __init__(self):
        super().__init__() 
        self.__hourly_rate = 50.0

    def calculate_fee(self, exit_time: datetime) -> float:
        duration = exit_time - self.get_entry_time()
        hours = max(1, int(duration.total_seconds() / 3600))
        return hours * self.__hourly_rate

class Motorcycle(Vehicle):
    def __init__(self):
        super().__init__()
        self.__hourly_rate = 20.0

    def calculate_fee(self, exit_time: datetime) -> float:
        duration = exit_time - self.get_entry_time()
        hours = max(1, int(duration.total_seconds() / 3600))
        return hours * self.__hourly_rate

# ==========================================
# 3. COMPOSITION
# ==========================================
# 
class ParkingSpot:
    """
    Represents a single parking spot. 
    Manages its own state (Occupied/Empty) and the vehicle parked in it.
    """
    def __init__(self, spot_id: str):
        self.__spot_id = spot_id
        self.__is_occupied = False
        self.__parked_vehicle: Optional[Vehicle] = None

    def get_spot_id(self) -> str:
        return self.__spot_id

    def is_occupied(self) -> bool:
        return self.__is_occupied

    def get_parked_vehicle(self) -> Optional[Vehicle]:
        return self.__parked_vehicle

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.__is_occupied:
            self.__parked_vehicle = vehicle
            self.__is_occupied = True
            return True
        return False

    def remove_vehicle(self) -> Optional[Vehicle]:
        if self.__is_occupied:
            vehicle = self.__parked_vehicle
            self.__parked_vehicle = None
            self.__is_occupied = False
            return vehicle
        return None


class ParkingLot:
    """
    Manager class representing the entire parking lot.
    Contains a list of ParkingSpot objects (Composition).
    """
    def __init__(self, spot_names: List[str]):
        self.__spots: List[ParkingSpot] = []
        for name in spot_names:
            self.__spots.append(ParkingSpot(name))

    def find_available_spot(self) -> Optional[ParkingSpot]:
        for spot in self.__spots:
            if not spot.is_occupied():
                return spot
        return None

    def get_total_available_spots(self) -> int:
        return sum(1 for spot in self.__spots if not spot.is_occupied())

    def get_spot_by_id(self, spot_id: str) -> Optional[ParkingSpot]:
        for spot in self.__spots:
            if spot.get_spot_id() == spot_id:
                return spot
        return None