import cv2
import json
import os
import tkinter as tk
from tkinter import simpledialog

# Configuration
IMAGE_PATH = r"C:\Users\kemal\Desktop\Smart Parking Analysis & Prediction System\Footage\smart_parking_demo_sample_4.jpg"
OUTPUT_JSON = 'rois.json'

# Global variables
points = []
rois = {}

# Initialize Tkinter root window (hidden)
root = tk.Tk()
root.withdraw() # We only want the popup dialog, not the main empty window

def draw_rectangle(event, x, y, flags, param):
    global points, rois, img, clone

    # Left mouse button click (start drawing)
    if event == cv2.EVENT_LBUTTONDOWN:
        points = [(x, y)]

    # Left mouse button release (finish drawing)
    elif event == cv2.EVENT_LBUTTONUP:
        points.append((x, y))
        
        # Ensure coordinates are top-left and bottom-right
        x1, y1 = min(points[0][0], points[1][0]), min(points[0][1], points[1][1])
        x2, y2 = max(points[0][0], points[1][0]), max(points[0][1], points[1][1])
        
        # 1. Draw a temporary RED rectangle to show current selection
        temp_img = img.copy()
        cv2.rectangle(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.imshow("Parking Calibration", temp_img)
        cv2.waitKey(1) # Force UI update before opening the dialog
        
        # 2. Open a UI dialog box to get the spot name
        spot_name = simpledialog.askstring(
            "Spot Name", 
            "Enter the name for this parking spot (e.g., A1, B2):", 
            parent=root
        )
        
        # 3. If user entered a name and clicked OK
        if spot_name and spot_name.strip() != "":
            spot_name = spot_name.strip()
            rois[spot_name] = [x1, y1, x2, y2]
            
            # Draw a permanent GREEN rectangle and add the text label
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, spot_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow("Parking Calibration", img)
            print(f"[+] '{spot_name}' successfully saved.")
        else:
            # If user clicked Cancel or left it empty, revert to original image
            cv2.imshow("Parking Calibration", img)
            print("[-] Selection cancelled.")

# Load the image
if not os.path.exists(IMAGE_PATH):
    print(f"ERROR: '{IMAGE_PATH}' not found. Please place a parking lot image in the directory.")
    exit()

img = cv2.imread(IMAGE_PATH)
clone = img.copy()

cv2.namedWindow("Parking Calibration")
cv2.setMouseCallback("Parking Calibration", draw_rectangle)

print("="*50)
print(" SMART PARKING UI CALIBRATION TOOL")
print("="*50)
print("1. Draw a box over a parking spot.")
print("2. A popup window will appear. Type the spot name and press OK.")
print("3. Press 'q' on your keyboard to save all spots and exit.")
print("="*50)

while True:
    cv2.imshow("Parking Calibration", img)
    key = cv2.waitKey(1) & 0xFF
    
    # Break the loop and save if 'q' is pressed
    if key == ord("q"):
        break

# Save to JSON file
with open(OUTPUT_JSON, 'w') as f:
    json.dump(rois, f, indent=4)

print(f"\nGreat! All parking spot coordinates have been successfully saved to '{OUTPUT_JSON}'.")
cv2.destroyAllWindows()