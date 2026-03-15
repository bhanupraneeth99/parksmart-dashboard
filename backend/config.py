import os
from datetime import datetime

START_TIME = datetime.utcnow()

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Global Configurations
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "yolo11n.pt"))
MODEL_IMG_SIZE = 640
MAX_VIDEO_SIZE_MB = 500
DEBUG_PIPELINE = os.getenv("DEBUG_PIPELINE", "True").lower() == "true"

# 12. Performance Constraints (User specified)
QUEUE_LIMIT = 50
MAX_FPS_PROCESSING = 10
CONFIDENCE_THRESHOLD = 0.25
SLOT_STATE_COOLDOWN_SEC = 1
HASH_DISTANCE_THRESHOLD = 5
MAX_HASH_SKIP_FRAMES = 3
FORCE_DETECTION_INTERVAL = 5
PROCESSING_LATENCY_WINDOW = 10
FPS_STABILITY_WINDOW = 30

# Additional Stability Settings
YOLO_WARMUP_FRAMES = 5
MEMORY_WARNING_MB = 1500
MEMORY_RESTART_MB = 2000
MAX_STREAM_RETRIES = 5
TRACK_LOST_TIMEOUT = 3
TRACKER_MAP_TTL = 10 # Seconds

# Stream Sources
PRIMARY_STREAM_URL = os.getenv("PRIMARY_STREAM_URL", "")
FALLBACK_STREAM_URL = os.getenv("FALLBACK_STREAM_URL", "")
DEBUG_STREAM_ENABLED = os.getenv("DEBUG_STREAM_ENABLED", "True").lower() == "true"

ALLOWED_VEHICLE_CLASSES = ["car", "truck", "bus", "motorcycle", "cell phone"]
YOLO_VEHICLE_CLASS_IDS = [2, 3, 5, 7, 67] # COCO: car, motorcycle, bus, truck, cell phone (top-down bias)
