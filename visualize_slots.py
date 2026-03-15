import cv2
import numpy as np
import sqlite3
import json
import os

ROOT_DIR = r"d:\parksmart-dashboard"
VIDEO_PATH = os.path.join(ROOT_DIR, "parking_video.mp4")
DB_PATH = os.path.join(ROOT_DIR, "backend", "parksmart.db")

DESIGN_WIDTH = 960
DESIGN_HEIGHT = 540

def visualize():
    print(f"Reading DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, polygon FROM parking_slots")
    slots = cursor.fetchall()
    conn.close()

    cap = cv2.VideoCapture(VIDEO_PATH)
    for _ in range(100): cap.read()
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Could not read frame")
        return

    h, w = frame.shape[:2]
    scale_x = w / DESIGN_WIDTH
    scale_y = h / DESIGN_HEIGHT
    print(f"Resolution: {w}x{h}, Scale: {scale_x:.2f}x{scale_y:.2f}")

    for sid, poly_str in slots:
        poly_pts = json.loads(poly_str)
        scaled_pts = [[int(x * scale_x), int(y * scale_y)] for [x, y] in poly_pts]
        pts_array = np.array(scaled_pts, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts_array], True, (0, 255, 0), 3)
        # Put ID text
        cx = int(np.mean([p[0] for p in scaled_pts]))
        cy = int(np.mean([p[1] for p in scaled_pts]))
        cv2.putText(frame, sid, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    output_path = os.path.abspath("polygon_check.jpg")
    cv2.imwrite(output_path, frame)
    print(f"Saved visualization to {output_path}")

if __name__ == "__main__":
    visualize()
