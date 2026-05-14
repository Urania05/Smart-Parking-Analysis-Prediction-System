import streamlit as st
import requests
from PIL import Image
import io
import joblib
import pandas as pd
import datetime

# Configure page layout
st.set_page_config(layout="wide", page_title="Smart Parking Dashboard", page_icon="🚗")

# Load machine learning model
@st.cache_resource
def load_ml_model():
    try:
        return joblib.load('parking_model.pkl')
    except FileNotFoundError:
        return None

ml_model = load_ml_model()

# --- SECURITY AND ACCESS (RBAC) ---
st.sidebar.header("🔐 Security Access")
st.sidebar.write("Staff Only. Customers leave blank.")
api_key = st.sidebar.text_input("Enter API Key:", type="password")

api_headers = {}
if api_key:
    api_headers["X-API-Key"] = api_key

# ==========================================
# VIEW ROUTING (CUSTOMER VS STAFF)
# ==========================================

if not api_key:
    # --- CUSTOMER VIEW ---
    st.title("Smart Parking - Welcome")
    st.markdown("---")
    
    # Fetch real-time parking status from backend
    try:
        response = requests.get("http://127.0.0.1:8000/status/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            available_spots = data.get("available", 0)
        else:
            available_spots = 0
    except Exception:
        available_spots = 0

    # If spots are available
    if available_spots > 0:
        st.info(f"Current Available Spots: **{available_spots}**")
        
        # Fetch a real spot from the database and store it in session state
        if 'assigned_spot' not in st.session_state:
            try:
                assign_response = requests.post("http://127.0.0.1:8000/assign-spot/", timeout=2)
                if assign_response.status_code == 200:
                    st.session_state.assigned_spot = assign_response.json().get("assigned_spot")
                else:
                    st.session_state.assigned_spot = "Please contact staff."
            except Exception:
                st.session_state.assigned_spot = "Connection Error"
            
        st.success(f"Assigned Parking Spot: **{st.session_state.assigned_spot}**")
        st.write("Please proceed to your assigned spot. Have a great day!")
        
    # If parking is full or backend is offline
    else:
        st.error("Sorry, the parking lot is currently FULL or offline.")
        st.write("Please wait for a vehicle to exit.")
    
    st.caption("*(Note: This is the customer-facing view. Staff must login via sidebar.)*")

else:
    # --- STAFF VIEW ---
    st.title("🎛️ Parking Management Dashboard")
    st.write("Monitor real-time camera feeds, predict future availability, and view system logs.")
    
    tab_live, tab_predict, tab_logs = st.tabs([
        "📷 Real-Time Detection", 
        "📈 AI Forecast Dashboard", 
        "📋 System Logs (Admin)"
    ])

    # TAB 1: REAL-TIME COMPUTER VISION (YOLOv8)
    with tab_live:
        st.header("Live Camera Analysis")
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
                    
                    files_json = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    response_json = requests.post(API_URL_JSON, headers=api_headers, files=files_json)
                    
                    files_img = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    response_img = requests.post(API_URL_IMAGE, headers=api_headers, files=files_img)
                    
                    if response_json.status_code == 200 and response_img.status_code == 200:
                        data = response_json.json()
                        
                        with col2:
                            st.subheader("Live Detection Results")
                            result_image = Image.open(io.BytesIO(response_img.content))
                            st.image(result_image, use_container_width=True)
                            
                            st.markdown("### Analytics Summary")
                            summary = data["summary"]
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Total Monitored", summary["total_monitored_spaces"])
                            m2.metric("Available", summary["empty_spaces"])
                            m3.metric("Occupied", summary["occupied_spaces"])
                    elif response_json.status_code == 401 or response_img.status_code == 401:
                         st.error("API Error: Unauthorized.")
                    else:
                        st.error(f"API Error: Status Code {response_json.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to Backend. Ensure FastAPI is running.")

    # TAB 2: FUTURE PREDICTION (BI DASHBOARD)
    with tab_predict:
        st.header("Forecast Dashboard (Next 24 Hours)")
        st.write("Business Intelligence view of predicted parking lot occupancy based on machine learning.")
        
        if ml_model is None:
            st.error("Machine Learning model not found! Please place 'parking_model.pkl' in the project directory.")
        else:
            try:
                status_req = requests.get("http://127.0.0.1:8000/status/", timeout=2)
                total_spaces = status_req.json().get("total_spots", 10)
            except:
                total_spaces = 10
            
            now = datetime.datetime.now()
            forecast_data = []
            
            for i in range(24):
                future_time = now + datetime.timedelta(hours=i)
                day_of_week = future_time.weekday()
                hour = future_time.hour
                is_weekend = 1 if day_of_week >= 5 else 0
                
                input_df = pd.DataFrame({
                    'day_of_week': [day_of_week],
                    'hour': [hour],
                    'is_weekend': [is_weekend]
                })
                
                prediction = ml_model.predict(input_df)[0]
                predicted_occupied = max(0, min(total_spaces, int(round(prediction))))
                
                forecast_data.append({
                    "Time": future_time.strftime("%H:00"),
                    "Day": future_time.strftime("%A"),
                    "Occupied": predicted_occupied,
                    "Available": total_spaces - predicted_occupied
                })
                
            df_forecast = pd.DataFrame(forecast_data)
            
            st.subheader("Key Performance Indicators")
            
            peak_hour_idx = df_forecast["Occupied"].idxmax()
            quiet_hour_idx = df_forecast["Occupied"].idxmin()
            
            peak_hour = df_forecast.iloc[peak_hour_idx]
            quiet_hour = df_forecast.iloc[quiet_hour_idx]
            current_status = df_forecast.iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                label="Expected Peak Hour", 
                value=f"{peak_hour['Time']} ({peak_hour['Day'][:3]})", 
                delta=f"{peak_hour['Occupied']} Spots Filled",
                delta_color="inverse"
            )
            
            col2.metric(
                label="Most Available Hour", 
                value=f"{quiet_hour['Time']} ({quiet_hour['Day'][:3]})", 
                delta=f"{quiet_hour['Available']} Spots Empty",
                delta_color="normal"
            )
            
            col3.metric(
                label="Current Hour Forecast", 
                value=f"{current_status['Occupied']} Occupied", 
                delta=f"{int((current_status['Occupied']/total_spaces)*100)}% Full",
                delta_color="off"
            )
            
            st.markdown("---")
            
            st.subheader("📊 24-Hour Occupancy Trend")
            chart_data = df_forecast.set_index("Time")[["Occupied"]]
            st.area_chart(chart_data, color="#FF4B4B")
            
            st.info("💡 **Insight:** The chart above shows the estimated number of occupied spots over the next 24 hours. Use this data to optimize staff shifts or adjust pricing.")

    # TAB 3: SYSTEM LOGS (ADMIN ONLY)
    with tab_logs:
        st.header("📋 Parking Logs")
        st.write("View historical parking entries, exits, and fee calculations.")
        
        if st.button("Fetch System Logs"):
            response = requests.get("http://127.0.0.1:8000/logs/", headers=api_headers)
            
            if response.status_code == 200:
                st.success("Access Granted! Loading logs...")
                logs = response.json()
                st.dataframe(logs, use_container_width=True)
                
            elif response.status_code == 401:
                st.error("Unauthorized: Operators cannot view logs. Admin privileges are required.")
                
            elif response.status_code == 403:
                st.error("Invalid Access: The API key provided is incorrect.")
                
            else:
                st.error(f"System connection failed. Status Code: {response.status_code}")