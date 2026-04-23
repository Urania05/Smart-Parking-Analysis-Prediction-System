## Risk Identification & Assessment
For the Smart Parking System, we have identified potential risks across technical, hardware, and project management domains.

* **Risk 1 (Technical - CV):** Low detection accuracy due to poor lighting, shadows, or bad weather conditions (rain/snow).
* **Risk 2 (Hardware - IoT):** IP Camera connection failures or physical damage to the camera lens.
* **Risk 3 (System - Backend):** High latency in API responses causing the real-time dashboard to lag.
* **Risk 4 (Project Management):** Scope creep and time constraints preventing the completion of the MVP within the 14-week semester.

### Mitigation & Preventive Actions
* **Mitigation 1 (CV):** Use a diverse dataset (like PKLot) that includes various weather and lighting conditions to train the OpenCV model robustly.
* **Mitigation 2 (Hardware):** Implement a "connection timeout" alert in the backend to immediately notify the System Admin if a camera goes offline.
* **Mitigation 3 (System):** Optimize the Python backend (FastAPI/Flask) and resize video frames before processing to reduce CPU load and latency.
* **Mitigation 4 (Project):** Strictly adhere to the Agile Sprint plan and enforce the MVP limitations defined in the Project Scope.

### Risk Matrix
*(Note: Score = Likelihood x Impact. Scale: 1-Low, 3-Medium, 5-High)*

| Risk ID | Risk Description | Likelihood (1-5) | Impact (1-5) | Risk Score | Risk Level |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **R01** | Poor weather reducing CV accuracy | 4 | 4 | 16 | High |
| **R02** | IP Camera offline/failure | 2 | 5 | 10 | Medium |
| **R03** | High API latency / Dashboard lag | 3 | 3 | 9 | Medium |
| **R04** | Failure to deliver MVP on time | 2 | 5 | 10 | Medium |

---

## Validation and Testing Plan
Since our project relies heavily on Machine Learning and real-time data flow, our testing strategy is divided into Model Validation and System Testing.

### 1. Model Validation
* **Methodology:** The dataset will be split into 80% training and 20% testing sets to prevent overfitting.
* **Evaluation Metrics:** The performance of the vehicle detection model will be evaluated using standard ML metrics:
  * **Accuracy:** Overall correctness of empty vs. occupied spot detection.
  * **Precision & Recall:** To minimize False Positives and False Negatives.

### 2. System and Integration Testing
* **API Testing:** Using tools like Postman to ensure the backend correctly sends JSON data to the frontend without data loss.
* **Load Testing:** Simulating multiple users accessing the web dashboard simultaneously to ensure the system does not crash under pressure.
* **Role-Based Access Control Testing:** Attempting to access the admin dashboard with a public user account to verify security restrictions.

---

## Success Criteria
To objectively determine whether the Smart Parking System project is successful at the end of the semester, the following criteria must be met:

* **Model Accuracy:** The detection module achieves a minimum of 85% accuracy in daylight conditions on the test dataset.
* **System Latency:** The system successfully updates the web dashboard within 2 seconds of a parking spot status changing.
* **Functional MVP:** The delivery of a working Minimum Viable Product, including camera feed integration, backend API, and a basic frontend dashboard, completed within the 14-week timeline.
* **RBAC Verification:** The system successfully distinguishes between a regular driver and an administrator.
