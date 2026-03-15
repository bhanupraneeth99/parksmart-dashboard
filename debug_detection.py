import cv2
import os
import torch
from ultralytics import YOLO
import sys

# Paths
ROOT_DIR = r"d:\parksmart-dashboard"
VIDEO_PATH = os.path.join(ROOT_DIR, "parking_video.mp4")
MODEL_PATH = os.path.join(ROOT_DIR, "backend", "models", "yolo11n.pt")

def debug():
    print(f"Checking video: {VIDEO_PATH}")
    if not os.path.exists(VIDEO_PATH):
        print("Error: Video file not found")
        return

    print(f"Loading model: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print("Error: Model file not found")
        return

    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    # Read 100th frame for stability
    for _ in range(100):
        cap.read()
    
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        return
    
    # Standard classes for COCO: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
    results = model.predict(frame, conf=0.25, imgsz=640)
    
    print(f"Found {len(results[0].boxes)} vehicles")
    for box in results[0].boxes:
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        xyxy = box.xyxy[0].cpu().numpy()
        print(f" - Class: {cls}, Conf: {conf:.2f}, Box: {xyxy}")

    # Save debug image
    debug_img_path = os.path.abspath("debug_shot.jpg")
    results[0].save(filename=debug_img_path)
    print(f"Saved debug image to {debug_img_path}")

    cap.release()

if __name__ == "__main__":
    debug()
