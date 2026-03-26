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
*Developed for Software Project Management Course*
