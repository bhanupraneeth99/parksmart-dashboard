import cv2
import numpy as np
import sqlite3
import json
import os
from shapely.geometry import Polygon

ROOT_DIR = r"d:\parksmart-dashboard"
VIDEO_PATH = os.path.join(ROOT_DIR, "parking_video.mp4")
DB_PATH = os.path.join(ROOT_DIR, "backend", "parksmart.db")

DESIGN_WIDTH = 960
DESIGN_HEIGHT = 540

def diagnose():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, polygon FROM parking_slots")
    slots = cursor.fetchall()
    conn.close()

    cap = cv2.VideoCapture(VIDEO_PATH)
    for _ in range(100): cap.read()
    ret, frame = cap.read()
    cap.release()
    
    h, w = frame.shape[:2]
    scale_x = w / DESIGN_WIDTH
    scale_y = h / DESIGN_HEIGHT
    
    # Mock some detections from the last run
    detections = [
        {"centroid": (1719, 799), "bbox": (1628, 567, 1811, 1031)},
        {"centroid": (409, 808), "bbox": (310, 585, 508, 1030)},
        {"centroid": (917, 816), "bbox": (820, 584, 1015, 1048)},
        {"centroid": (156, 829), "bbox": (62, 624, 251, 1034)},
        {"centroid": (1187, 875), "bbox": (1092, 684, 1282, 1066)},
        {"centroid": (682, 785), "bbox": (574, 511, 790, 1058)}
    ]

    print(f"Frame: {w}x{h}, Scale: {scale_x}x{scale_y}")
    for sid, status, poly_str in slots:
        poly_pts = json.loads(poly_str)
        scaled_pts = [[int(x * scale_x), int(y * scale_y)] for [x, y] in poly_pts]
        poly_cv2 = np.array(scaled_pts, dtype=np.int32).reshape((-1, 1, 2))
        
        print(f"\nSlot {sid} (Current DB Status: {status})")
        hits = 0
        for i, d in enumerate(detections):
            cx, cy = d["centroid"]
            is_inside = cv2.pointPolygonTest(poly_cv2, (float(cx), float(cy)), False) >= 0
            if is_inside:
                print(f"  - Hit by Detection {i} at ({cx}, {cy})")
                hits += 1
        if hits == 0:
            print("  - NO HITS")

if __name__ == "__main__":
    diagnose()
