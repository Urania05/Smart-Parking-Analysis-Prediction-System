from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
import io
from PIL import Image
import json
from oop_core import ParkingLot, Car

# Import database connection and model files
import models
import database

# Initialize the FastAPI application
app = FastAPI(
    title="Smart Parking API",
    description="Real-time vehicle detection and parking space analysis API using YOLOv8 with PostgreSQL.",
    version="1.0.0"
)

# Create tables in PostgreSQL on startup if they don't exist
models.Base.metadata.create_all(bind=database.engine)

# Load the YOLOv8 model
try:
    model = YOLO('best.pt')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

# --- PARKING SPOTS (ROIs) LOADING ---
# Dynamically load coordinates from our calibration file instead of hardcoding them.
try:
    with open('rois.json', 'r') as f:
        PARKING_SPOTS = json.load(f)
    print(f"Calibration file loaded successfully. Monitoring {len(PARKING_SPOTS)} parking spots.")
    
except FileNotFoundError:
    print("ERROR: 'rois.json' not found. Please run calibration.py script first.")
    PARKING_SPOTS = {}

lot_manager = ParkingLot(spot_names=list(PARKING_SPOTS.keys()))

# --- IoU CALCULATION FUNCTION ---
def calculate_iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    box format: [x1, y1, x2, y2]
    """
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0 # No intersection

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Parking API."}

@app.get("/spots/")
def get_spots(db: Session = Depends(database.get_db)):
    spots = db.query(models.ParkingSpot).all()
    return spots

@app.get("/logs/")
def get_logs(db: Session = Depends(database.get_db)):
    logs = db.query(models.ParkingLog).order_by(models.ParkingLog.id.desc()).limit(20).all()
    return logs

# ==========================================
# ENDPOINT 1: JSON DATA (DATABASE UPDATE)
# ==========================================
@app.post("/predict")
async def predict_parking(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        results = model.predict(source=img_cv, conf=0.4, save=False)[0]
        
        current_frame_status = {
            spot_id: {"is_occupied": False, "vehicle_class": "None"} 
            for spot_id in PARKING_SPOTS.keys()
        }
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id == 0: 
                continue 
                
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            yolo_box = [x1, y1, x2, y2]
            vehicle_class = model.names[class_id]
            
            best_iou = 0
            best_spot_id = None
            
            for spot_id, spot_coords in PARKING_SPOTS.items():
                iou = calculate_iou(yolo_box, spot_coords)
                if iou > best_iou:
                    best_iou = iou
                    best_spot_id = spot_id
            
            if best_spot_id and best_iou > 0.4:
                current_frame_status[best_spot_id]["is_occupied"] = True
                current_frame_status[best_spot_id]["vehicle_class"] = vehicle_class 
                
                spot = lot_manager.get_spot_by_id(best_spot_id)
                
                if spot and not spot.is_occupied():
                    new_vehicle = Car() 
                    spot.park_vehicle(new_vehicle)
                    print(f"OOP Log: Vehicle with ticket {new_vehicle.get_ticket_id()} entered spot {best_spot_id}.")

            for spot_id in PARKING_SPOTS.keys():
                spot = lot_manager.get_spot_by_id(spot_id)

                if spot and spot.is_occupied() and not current_frame_status[spot_id]["is_occupied"]:
                    departing_vehicle = spot.remove_vehicle()
                    if departing_vehicle:  # Araç gerçekten varsa
                        fee = departing_vehicle.calculate_fee(datetime.now())
                        print(f"OOP Log: Vehicle exited spot {spot_id}. Total Fee: ${fee}")

        detections_response = []
        occupied_count = 0
        empty_count = 0

        for spot_id, status_data in current_frame_status.items():
            is_occupied = status_data["is_occupied"]
            
            if is_occupied:
                occupied_count += 1
            else:
                empty_count += 1

            spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.spot_number == spot_id).first()
            if not spot:
                spot = models.ParkingSpot(spot_number=spot_id, is_occupied=is_occupied)
                db.add(spot)
                db.commit()
                db.refresh(spot)

            if spot.is_occupied != is_occupied:
                spot.is_occupied = is_occupied
                spot.last_updated = datetime.utcnow()

                if is_occupied:
                    new_log = models.ParkingLog(spot_number=spot_id, vehicle_class=status_data["vehicle_class"])
                    db.add(new_log)
                else:
                    last_log = db.query(models.ParkingLog).filter(
                        models.ParkingLog.spot_number == spot_id, 
                        models.ParkingLog.exit_time == None
                    ).order_by(models.ParkingLog.id.desc()).first()
                    
                    if last_log:
                        last_log.exit_time = datetime.utcnow()

                db.commit()

            detections_response.append({
                "spot_number": spot_id,
                "status": "occupied" if is_occupied else "empty",
                "coordinates": PARKING_SPOTS[spot_id]
            })
            
        return JSONResponse(content={
            "success": True,
            "summary": {
                "total_monitored_spaces": len(PARKING_SPOTS),
                "empty_spaces": empty_count,
                "occupied_spaces": occupied_count
            },
            "spots_status": detections_response
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# ==========================================
# ENDPOINT 2: VISUAL DATA (DRAWN IMAGE)
# ==========================================
@app.post("/predict-image")
async def predict_parking_image(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        results = model.predict(source=img_cv, conf=0.4, save=False)[0]
        
        current_frame_status = {
            spot_id: {"is_occupied": False} 
            for spot_id in PARKING_SPOTS.keys()
        }
        
        # YOLO Detection and IoU Intersection
        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id == 0: continue 
                
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            yolo_box = [x1, y1, x2, y2]
            
            best_iou = 0
            best_spot_id = None
            
            for spot_id, spot_coords in PARKING_SPOTS.items():
                iou = calculate_iou(yolo_box, spot_coords)
                if iou > best_iou:
                    best_iou = iou
                    best_spot_id = spot_id
            
            if best_spot_id and best_iou > 0.4:
                current_frame_status[best_spot_id]["is_occupied"] = True
                
                spot = lot_manager.get_spot_by_id(best_spot_id)
                
                if spot and not spot.is_occupied():
                    new_vehicle = Car() 
                    spot.park_vehicle(new_vehicle)

        for spot_id in PARKING_SPOTS.keys():
            spot = lot_manager.get_spot_by_id(spot_id)

            if spot and spot.is_occupied() and not current_frame_status[spot_id]["is_occupied"]:
                departing_vehicle = spot.remove_vehicle()
                if departing_vehicle:  
                    fee = departing_vehicle.calculate_fee(datetime.now())

        # Draw on Image (Red/Green Boxes)
        for spot_id, coords in PARKING_SPOTS.items():
            x1, y1, x2, y2 = coords
            is_occupied = current_frame_status[spot_id]["is_occupied"]
            
            if is_occupied:
                color = (0, 0, 255)  # Red (in BGR format)
                label = f"{spot_id} (Occupied)"
            else:
                color = (0, 255, 0)  # Green
                label = f"{spot_id} (Empty)"
                
            cv2.rectangle(img_cv, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(img_cv, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Return the drawn image as JPEG
        _, encoded_img = cv2.imencode('.jpg', img_cv)
        return Response(content=encoded_img.tobytes(), media_type="image/jpeg")

    except Exception as e:
        print(f"\n[ERROR] /predict-image failed: {str(e)}\n")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})