@echo off
echo =========================================
echo SMART PARKING SISTEMI BASLATILIYOR...
echo =========================================

echo [1/2] Arka Uc (FastAPI) Ayaga Kaldiriliyor...
start cmd /k "uvicorn main:app --reload"

:: Arka ucun baslamasi icin 3 saniye bekleme (Opsiyonel ama sagliklidir)
timeout /t 3 /nobreak > NUL

echo [2/2] On Uc (Streamlit) Ayaga Kaldiriliyor...
start cmd /k "streamlit run app.py"

echo Sistem basariyla tetiklendi! Bu pencereyi kapatabilirsiniz.
exit