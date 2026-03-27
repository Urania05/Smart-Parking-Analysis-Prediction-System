@echo off
echo =======================================================
echo  Starting Smart Parking Analysis System MVP...
echo  Engine: YOLOv8 Nano ^| Interface: Streamlit
echo =======================================================
echo.

if exist venv\Scripts\activate (
    echo Activating Virtual Environment...
    call venv\Scripts\activate
)

echo Launching the Dashboard...
timeout /t 2 /nobreak > NUL

streamlit run app.py

pause