import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Parking Analysis System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- TITLE AND DESCRIPTION ---
st.title("🚗 Smart Parking Analysis System - MVP Demo")
st.markdown("""
Welcome to the live demonstration of the **Smart Parking Analysis System**.
This system utilizes a custom-trained **YOLOv8 Nano** model, trained on the PKLot dataset (achieving ~99% mAP), to detect vehicles and determine parking spot status in real-time.

---
""")

# --- LOAD MODEL (Cached to avoid reloading) ---
@st.cache_resource
def load_yolo_model():
    # Assumes 'best.pt' is in the current directory or provide the full path
    try:
        model = YOLO('best.pt')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}. Make sure 'best.pt' is in the project directory.")
        return None

# Load the trained brain
model = load_yolo_model()

# --- MAIN SECTION: FILE UPLOADER ---
st.header("1. Upload Parking Lot Image")
uploaded_file = st.file_uploader("Choose a JPG/PNG file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display a spinner during processing
    with st.spinner('AI Brain is analyzing the image... please wait...'):
        
        # --- PRE-PROCESSING ---
        # Load the image using PIL
        image = Image.open(uploaded_file)
        
        # Convert PIL image to NumPy array (RGB)
        img_array = np.array(image)
        
        # Convert to OpenCV format (BGR) for YOLO inference
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # --- AI INFERENCE ---
        # Run YOLOv8 prediction (using conf=0.4 balance from testing)
        results = model.predict(source=img_cv, conf=0.4, save=False)[0]
        
        # Initialize counters
        empty_spaces = 0
        occupied_spaces = 0
        
        # --- POST-PROCESSING & VISUALIZATION ---
        # Draw on the BGR image (OpenCV style)
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Define colors and labels (BGR)
            if class_id == 0: # Empty
                empty_spaces += 1
                color = (0, 255, 0) # Green
                label = f"Empty ({conf:.2f})"
            else: # Occupied
                occupied_spaces += 1
                color = (0, 0, 255) # Red
                label = f"Occupied ({conf:.2f})"
            
            # Draw standard rectangular box (no orientation needed for MVP demo)
            cv2.rectangle(img_cv, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img_cv, (x1, y1 - 20), (x1 + w, y1), color, -1)
            
            # Draw white text
            cv2.putText(img_cv, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Convert back to RGB for Streamlit display
        processed_img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        
        # --- UI LAYOUT: RESULTS & METRICS ---
        st.header("2. Real-Time Analysis Results")
        
        # Create columns for image and metrics
        col_img, col_metrics = st.columns([2, 1])
        
        with col_img:
            st.image(processed_img_rgb, caption='AI Analysis Result', use_container_width=True)
            
        with col_metrics:
            st.subheader("System Metrics")
            total_spaces = empty_spaces + occupied_spaces
            st.metric(label="Total Spaces Detected", value=total_spaces)
            
            c1, c2 = st.columns(2)
            c1.metric(label="Empty Spaces ✅", value=empty_spaces)
            c2.metric(label="Occupied Spaces 🚗", value=occupied_spaces)
            
            st.info(f"YOLO found {empty_spaces} empty and {occupied_spaces} occupied spots.")
            
            # Show Raw Detections (optional)
            if st.checkbox('Show raw detections JSON'):
                st.json(results.to_json())
                
else:
    st.info("Please upload an image to see the smart parking analysis in action!")
