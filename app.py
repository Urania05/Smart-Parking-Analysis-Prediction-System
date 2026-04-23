import streamlit as st
import requests
from PIL import Image
import io
import joblib
import pandas as pd
import datetime

# Configure the page layout
st.set_page_config(layout="wide", page_title="Smart Parking Dashboard", page_icon="🚗")

st.title("🚗 Smart Parking Management System")
st.write("Monitor real-time camera feeds and predict future parking availability using AI.")

# --- LOAD MACHINE LEARNING MODEL ---
# Using st.cache_resource so the model loads only once, keeping the app fast
@st.cache_resource
def load_ml_model():
    try:
        return joblib.load('parking_model.pkl')
    except FileNotFoundError:
        return None

ml_model = load_ml_model()

# --- CREATE TABS FOR UI ---
tab_live, tab_predict = st.tabs(["📷 Real-Time Detection", "🔮 Future Prediction"])

# ==========================================
# TAB 1: REAL-TIME COMPUTER VISION (YOLOv8)
# ==========================================
with tab_live:
    st.header("Live Camera Analysis")
    # FastAPI backend URLs
    API_URL_JSON = "http://127.0.0.1:8000/predict"
    API_URL_IMAGE = "http://127.0.0.1:8000/predict-image"

    uploaded_file = st.file_uploader("Choose a parking lot image for live detection...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Camera Feed")
            original_image = Image.open(uploaded_file)
            st.image(original_image, use_container_width=True)
            
        with st.spinner("Analyzing parking spaces with YOLOv8..."):
            try:
                file_bytes = uploaded_file.getvalue()
                
                # Request JSON data and Image data
                files_json = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                response_json = requests.post(API_URL_JSON, files=files_json)
                
                files_img = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                response_img = requests.post(API_URL_IMAGE, files=files_img)
                
                if response_json.status_code == 200 and response_img.status_code == 200:
                    data = response_json.json()
                    
                    with col2:
                        st.subheader("Live Detection Results")
                        result_image = Image.open(io.BytesIO(response_img.content))
                        st.image(result_image, use_container_width=True)
                        
                        st.markdown("### 📊 Analytics Summary")
                        summary = data["summary"]
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Total Monitored", summary["total_monitored_spaces"])
                        m2.metric("🟢 Available", summary["empty_spaces"])
                        m3.metric("🔴 Occupied", summary["occupied_spaces"])
                else:
                    st.error("API Error: Something went wrong during prediction.")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to Backend. Ensure FastAPI is running.")

# ==========================================
# TAB 2: FUTURE PREDICTION (RANDOM FOREST)
# ==========================================
# ==========================================
# TAB 2: FUTURE PREDICTION (RANDOM FOREST)
# ==========================================
with tab_predict:
    st.header("Forecast Parking Availability")
    
    if ml_model is None:
        st.error("🚨 Machine Learning model not found! Please place 'parking_model.pkl' in the project directory.")
    else:
        st.write("Select a future date and time to estimate how crowded the parking lot will be.")
        
        col_input, col_results = st.columns([1, 2])
        
        with col_input:
            st.subheader("Time Settings")
            target_date = st.date_input("Select Date", datetime.date.today())
            
            # --- YENİ MANUEL SAAT GİRİŞİ ---
            # Liste yerine sadece klavyeden 0-23 arası sayı girilen alan
            hour = st.number_input("Enter Hour (0-23)", min_value=0, max_value=23, value=12, step=1)
            
            # Extract features for the ML Model
            day_of_week = target_date.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            
            days_str = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            st.info(f"Targeting: **{days_str[day_of_week]}**, at **{hour}:00**")
            
            predict_btn = st.button("Generate Forecast 🚀", type="primary", use_container_width=True)
            
        if predict_btn:
            with col_results:
                st.subheader("AI Forecast Results")
                
                # Format inputs as a DataFrame for Scikit-Learn
                input_df = pd.DataFrame({
                    'day_of_week': [day_of_week],
                    'hour': [hour],
                    'is_weekend': [is_weekend]
                })
                
                # Get prediction
                prediction = ml_model.predict(input_df)[0]
                total_spaces = 44 # Based on our calibration
                
                # Round and logic checks
                predicted_occupied = int(round(prediction))
                predicted_occupied = max(0, min(total_spaces, predicted_occupied))
                predicted_empty = total_spaces - predicted_occupied
                
                # Display metrics
                r1, r2, r3 = st.columns(3)
                r1.metric("Total Spots", total_spaces)
                r2.metric("🟢 Expected Empty", predicted_empty)
                r3.metric("🔴 Expected Occupied", predicted_occupied)
                
                # Display visual progress bar
                occupancy_rate = int((predicted_occupied / total_spaces) * 100)
                st.progress(occupancy_rate / 100.0, text=f"Estimated Occupancy Rate: {occupancy_rate}%")
                
                # Simple insight message
                if occupancy_rate > 85:
                    st.warning("⚠️ High demand expected. Finding a spot might be difficult.")
                elif occupancy_rate < 30:
                    st.success("✅ Lots of spaces available. Easy parking expected.")
                else:
                    st.info("ℹ️ Moderate demand expected.")