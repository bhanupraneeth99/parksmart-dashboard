import cv2
import os
import torch
from ultralytics import YOLO

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_PATH = os.path.join(ROOT_DIR, "parking_video.mp4")
MODEL_PATH = os.path.join(ROOT_DIR, "backend", "models", "yolov8n.pt")
OUTPUT_DIR = os.path.join(ROOT_DIR, "debug_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Loading model from {MODEL_PATH}")
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Error: Could not open video at {VIDEO_PATH}")
    exit(1)

frame_indices = [0, 50, 100, 200, 300, 400, 500, 600]
for idx in frame_indices:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    if not ret:
        print(f"Could not read frame {idx}")
        continue
    
    results = model.predict(frame, imgsz=320, conf=0.1) # Low confidence for debug
    
    for i, r in enumerate(results):
        res_frame = r.plot()
        out_path = os.path.join(OUTPUT_DIR, f"frame_{idx}_det.jpg")
        cv2.imwrite(out_path, res_frame)
        print(f"Saved detection result to {out_path}")
        
cap.release()
print("Debug detection complete.")
