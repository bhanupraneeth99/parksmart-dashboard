from ultralytics import YOLO
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "backend", "models", "yolov8n.pt")

model = YOLO(MODEL_PATH)
print("--- Model Classes ---")
for id, name in model.names.items():
    if id < 10 or id in [67, 2, 3, 5, 7]:
        print(f"{id}: {name}")
print("Total classes:", len(model.names))
