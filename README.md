# Smart Parking Analysis System - MVP

## Project Overview
The Smart Parking Analysis System is a real-time computer vision project designed to detect vehicle presence in parking lots. This repository contains the Minimum Viable Product developed for the Software Project Management course. 

The system utilizes a custom-trained **YOLOv8 Nano** model on the PKLot dataset, integrated with a **FastAPI** backend and a **Streamlit** interactive dashboard.

## Project Management (Sprint Board)
Agile methodology was strictly followed during the development of this MVP. 
* [Click here to view our Sprint Board](https://github.com/EylulOzdemir/Smart-Parking-Analysis-Prediction-System)

## System Architecture
1. **AI Brain:** YOLOv8n
2. **Backend API:** FastAPI
3. **Frontend Dashboard:** Streamlit
4. **CI/CD:** GitHub Actions

## How to Run the Live Demo (Locally)

### 1. Install Dependencies
Make sure you have Python 3.10+ installed. Run the following command in your terminal:

`pip install -r requirements.txt`

### 2. Start the Backend & Frontend
To launch the interactive web dashboard, simply run:

`streamlit run app.py`

*The system will open a new browser window at http://localhost:8501. Upload a parking lot image from the test dataset to see the AI in action!*

---

## Risk Updates (Post-MVP Training Phase)
As part of our continuous risk management, we have updated our initial Risk Matrix based on the recent development sprint:

* **R01 (CV Accuracy) - UPDATE:** * *Initial State:* High Risk (Score: 16). 
  * *Current State:* **Low Risk (Score: 4).** * *Reason:* The custom YOLOv8 model trained on the PKLot dataset achieved an unexpectedly high mAP50 of 99%. The probability of the model failing to detect vehicles in standard CCTV angles has drastically decreased.



* **R04 (Failure to deliver MVP on time) - UPDATE:**
  * *Initial State:* Medium Risk (Score: 10).
  * *Current State:* **Resolved / Closed.**
  * *Reason:* The core MVP (Backend + Frontend + Model) has been successfully completed and deployed locally well within the 14-week constraint.

---

classDiagram
    %% Abstract Base Class
    class Vehicle {
        <<abstract>>
        -ticket_id: str
        -entry_time: datetime
        +get_ticket_id(): str
        +get_entry_time(): datetime
        +calculate_fee(exit_time: datetime)* float
    }

    %% Derived Class
    class Car {
        -hourly_rate: float
        +calculate_fee(exit_time: datetime): float
    }

    %% Spot Class
    class ParkingSpot {
        -spot_id: str
        -current_vehicle: Vehicle
        +get_spot_id(): str
        +is_occupied(): bool
        +park_vehicle(vehicle: Vehicle): void
        +remove_vehicle(): Vehicle
    }

    %% Manager Class
    class ParkingLot {
        -spots: List~ParkingSpot~
        +find_available_spot(): ParkingSpot
        +get_total_available_spots(): int
        +get_spot_by_id(spot_id: str): ParkingSpot
    }

    %% Relationships
    Vehicle <|-- Car : Inheritance (Kalıtım)
    ParkingSpot o-- Vehicle : Aggregation (Birleştirme)
    ParkingLot *-- ParkingSpot : Composition (Kompozisyon)

   
*Developed for Software Project Management Course*
