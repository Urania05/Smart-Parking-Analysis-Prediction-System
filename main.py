from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import cv2
import numpy as np
import io
from PIL import Image

# Initialize the FastAPI application
app = FastAPI(
    title="Smart Parking API",
    description="Real-time vehicle detection and parking space analysis API using YOLOv8.",
    version="1.0.0"
)

# Load the trained YOLOv8 model
# Note: Ensure your 'best.pt' file is in the same directory or provide the correct path
try:
    model = YOLO('best.pt')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Parking API. Send a POST request with an image to /predict."}

@app.post("/predict")
async def predict_parking(file: UploadFile = File(...)):
    try:
        # Read the uploaded image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert PIL Image to OpenCV format (numpy array)
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Run YOLOv8 inference
        # conf=0.4 ensures we only get confident predictions
        results = model.predict(source=img_cv, conf=0.4, save=False)[0]
        
        empty_spaces = 0
        occupied_spaces = 0
        detections = []
        
        # Parse the results
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # Coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            status = "empty" if class_id == 0 else "occupied"
            
            if class_id == 0:
                empty_spaces += 1
            else:
                occupied_spaces += 1
                
            detections.append({
                "status": status,
                "confidence": round(confidence, 2),
                "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })
            
        # Return the structured data to the frontend or dashboard
        return JSONResponse(content={
            "success": True,
            "summary": {
                "total_spaces": empty_spaces + occupied_spaces,
                "empty_spaces": empty_spaces,
                "occupied_spaces": occupied_spaces
            },
            "detections": detections
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# To run the server locally:
# uvicorn main:app --reload