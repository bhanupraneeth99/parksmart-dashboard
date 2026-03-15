from ultralytics import YOLO
import os

ROOT_DIR = r"d:\parksmart-dashboard"
MODEL_DIR = os.path.join(ROOT_DIR, "backend", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

model_name = "yolo11n.pt"
target_path = os.path.join(MODEL_DIR, model_name)

print(f"Downloading {model_name} to {target_path}...")
model = YOLO(model_name)
# This will download it to current dir if not found, then we move it
if os.path.exists(model_name):
    import shutil
    shutil.move(model_name, target_path)
    print("Download and move complete.")
else:
    # If it was already in a central cache, we can just save it
    model.save(target_path)
    print("Model saved to target path.")
