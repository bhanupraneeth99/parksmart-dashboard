import cv2
import numpy as np
from ultralytics import YOLO
import logging
import time
import torch
from database import SessionLocal
from models import ParkingSlot
from collections import deque

logging.basicConfig(level=logging.INFO)

# Global YOLO model loaded once on startup
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    global_model = YOLO('yolov8n.pt').to(device)
    logging.info(f"YOLOv8 model loaded successfully globally on {device}.")
except Exception as e:
    global_model = None
    logging.error(f"Failed to load global YOLO model: {e}")

# Warm-up inference to eliminate first-frame latency
if global_model is not None:
    try:
        logging.info("Performing YOLOv8 warm-up inference...")
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        with torch.no_grad():
            global_model(dummy_frame, verbose=False)
        logging.info("YOLOv8 warm-up complete.")
    except Exception as e:
        logging.warning(f"Failed to perform YOLOv8 warm-up: {e}")

# Global state for analysis status and streaming
# Global state for analysis status and streaming
analysis_status = {"status": "idle"}
analysis_paused = False
analysis_running = False
latest_frame = None

# EXIT LINE configuration
EXIT_LINE_Y = 380
vehicle_track_y = {}
vehicle_slot_assignment = {}
vehicle_last_seen_frame = {}

# Debug mode toggle for visual center detection overlays
DEBUG_MODE = False

# Temporal smoothing buffers & cooldown trackers for 7 slots
slot_detection_buffers = {f"S{i}": deque(maxlen=5) for i in range(1, 8)}
slot_last_seen_time = {f"S{i}": 0.0 for i in range(1, 8)}
slot_first_seen_time = {f"S{i}": 0.0 for i in range(1, 8)}

def set_analysis_paused(paused: bool):
    global analysis_paused, analysis_status
    analysis_paused = paused
    if paused:
        analysis_status["status"] = "stopped"
    else:
        analysis_status["status"] = "processing"

def get_video_stream():
    global latest_frame
    while True:
        if analysis_status["status"] == "idle" or latest_frame is None:
            time.sleep(1)
            continue
            
        ret, buffer = cv2.imencode('.jpg', latest_frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)

# Manual Polygon Calibration matching the real video feed
SLOT_POLYGONS = {
    # Sample calibration: Top-Left, Top-Right, Bottom-Right, Bottom-Left coordinates
    "S1": np.array([(100, 320), (220, 320), (200, 520), (50, 520)], np.int32).reshape((-1, 1, 2)),
    "S2": np.array([(240, 320), (360, 320), (340, 520), (210, 520)], np.int32).reshape((-1, 1, 2)),
    "S3": np.array([(380, 320), (500, 320), (480, 520), (350, 520)], np.int32).reshape((-1, 1, 2)),
    "S4": np.array([(520, 320), (640, 320), (620, 520), (490, 520)], np.int32).reshape((-1, 1, 2)),
    "S5": np.array([(660, 320), (780, 320), (760, 520), (630, 520)], np.int32).reshape((-1, 1, 2)),
    "S6": np.array([(800, 320), (920, 320), (900, 520), (770, 520)], np.int32).reshape((-1, 1, 2)),
    "S7": np.array([(940, 320), (1060, 320), (1040, 520), (910, 520)], np.int32).reshape((-1, 1, 2)),
}

def process_video(video_path: str):
    global analysis_status, latest_frame, analysis_running, slot_detection_buffers
    
    analysis_running = True
    analysis_status["status"] = "processing"
    
    try:
        logging.info(f"Starting YOLOv8 parking detection on {video_path}...")
    
        # Reset buffers and cooldowns on new video start
        for k in slot_detection_buffers.keys():
            slot_detection_buffers[k].clear()
            slot_last_seen_time[k] = 0.0
            slot_first_seen_time[k] = 0.0
        vehicle_track_y.clear()
        vehicle_slot_assignment.clear()
        vehicle_last_seen_frame.clear()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Could not open video source: {video_path}")
            analysis_status["status"] = "error"
            analysis_running = False
            return

        frame_count = 0
        latest_results = None
    
        while True:
            if analysis_paused:
                time.sleep(1)
                continue
                
            ret, frame = cap.read()
            if not ret:
                # Video stream ended, rewind to beginning for continuous Demo playing
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            frame = cv2.resize(frame, (960, 540))

            frame_count += 1
            
            # Only process YOLO on every 10th frame to save compute
            if frame_count % 10 == 0 or latest_results is None:
                # Optimize inference by omitting gradient trackers
                with torch.no_grad():
                    results = global_model.track(frame, persist=True, conf=0.4, verbose=False)
                latest_results = results
            
                detected_vehicles = []
                slots_to_free = []
                
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        track_id = int(box.id[0]) if box.id is not None else -1
                        
                        # Strict validation: Only count cars (2), motorcycles (3), buses (5), and trucks (7)
                        if cls_id in [2, 3, 5, 7]:
                            # Confidence validation
                            if conf < 0.4:
                                continue
                                
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            # Size validation
                            box_area = (x2 - x1) * (y2 - y1)
                            if box_area < 2000:
                                continue
                                
                            cx = int((x1 + x2) / 2)
                            cy = int((y1 + y2) / 2)
                            detected_vehicles.append((cx, cy, track_id))
                            
                            # Exit line tracking
                            if track_id != -1:
                                if track_id in vehicle_track_y:
                                    prev_cy = vehicle_track_y[track_id]
                                    # Crossed exit line from top to bottom
                                    if prev_cy < EXIT_LINE_Y and cy >= EXIT_LINE_Y:
                                        if track_id in vehicle_slot_assignment:
                                            slots_to_free.append(vehicle_slot_assignment[track_id])
                                vehicle_track_y[track_id] = cy
                                vehicle_last_seen_frame[track_id] = frame_count

                # Cleanup tracks not seen for 30 frames
                to_delete = [tid for tid, f in vehicle_last_seen_frame.items() if frame_count - f > 30]
                for tid in to_delete:
                    vehicle_track_y.pop(tid, None)
                    vehicle_slot_assignment.pop(tid, None)
                    vehicle_last_seen_frame.pop(tid, None)
                
                # Check DB
                db = SessionLocal()
                try:
                    slots = db.query(ParkingSlot).all()
                    db_changed = False
                    for slot in slots:
                        if slot.status in ["reserved"]:
                            continue
                    
                        poly = SLOT_POLYGONS.get(slot.id)
                        if poly is not None:
                            # Calculate slot center
                            M = cv2.moments(poly)
                            if M['m00'] != 0:
                                slot_cx = int(M['m10'] / M['m00'])
                                slot_cy = int(M['m01'] / M['m00'])
                            else:
                                slot_cx, slot_cy = poly[0][0][0], poly[0][0][1]
                                
                            vehicle_in_poly = False
                            closest_dist = float('inf')
                            
                            # Find closest detecting box to slot center if multiple overlap
                            assigned_track_id = -1
                            for (cx, cy, t_id) in detected_vehicles:
                                if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
                                    dist = (cx - slot_cx)**2 + (cy - slot_cy)**2
                                    if dist < closest_dist:
                                        closest_dist = dist
                                        vehicle_in_poly = True
                                        assigned_track_id = t_id
                                        
                            current_time = time.time()
                            
                            if vehicle_in_poly:
                                if slot_first_seen_time[slot.id] == 0.0:
                                    slot_first_seen_time[slot.id] = current_time
                                
                                # Update last seen to enforce the 0.5s cooldown when it leaves
                                slot_last_seen_time[slot.id] = current_time
                            else:
                                # Reset dwell timer once a vehicle fully leaves
                                slot_first_seen_time[slot.id] = 0.0
                                    
                            # Temporal smoothing: add to buffer
                            slot_detection_buffers[slot.id].append(1 if vehicle_in_poly else 0)
                            
                            # Only switch state if buffer is mature and strongly agrees
                            if len(slot_detection_buffers[slot.id]) == 5:
                                recent_occupancy = sum(slot_detection_buffers[slot.id])
                                
                                new_status = slot.status
                                
                                # If vehicle detected in >=3 of last 5 frames -> check dwell criteria
                                if recent_occupancy >= 3:
                                    # Ensure vehicle has been dwelling inside for at least 0.5s
                                    if current_time - slot_first_seen_time[slot.id] >= 0.5:
                                        new_status = "occupied"
                                        
                                # If vehicle detected in <=1 of last 5 frames -> check cooldown criteria
                                elif recent_occupancy <= 1:
                                    if current_time - slot_last_seen_time[slot.id] < 1.0:
                                        # Buffer cooldown -> 1.0s buffer before clearing to available
                                        new_status = "occupied"
                                    else:
                                        new_status = "available"
                                    
                                if slot.status != new_status:
                                    logging.info(f"Slot {slot.id} status changed from {slot.status} to {new_status}")
                                    slot.status = new_status
                                    db_changed = True
                                    
                                if new_status == "occupied" and assigned_track_id != -1:
                                    vehicle_slot_assignment[assigned_track_id] = slot.id
                                    
                    # Apply forced exit-line free operations
                    for slot in slots:
                        if slot.id in slots_to_free and slot.status == "occupied":
                            slot.status = "available"
                            slot_detection_buffers[slot.id].clear()
                            slot_first_seen_time[slot.id] = 0.0
                            slot_last_seen_time[slot.id] = 0.0
                            db_changed = True
                            logging.info(f"Slot {slot.id} force-freed by Exit Line crossing")
                        
                    if db_changed:
                        db.commit()
                except Exception as e:
                    logging.error(f"Detection loop DB error: {e}")
                finally:
                    db.close()

            # Draw UI on every frame using latest polygons and boxes
            try:
                db = SessionLocal()
                slots = {s.id: s.status for s in db.query(ParkingSlot).all()}
                db.close()
            except:
                slots = {}

            for slot_id, poly in SLOT_POLYGONS.items():
                status = slots.get(slot_id, "available")
                
                if status == "available":
                    color = (255, 0, 0)      # Blue
                    label = f"{slot_id} - AVAILABLE"
                elif status == "reserved":
                    color = (0, 255, 255)    # Yellow in BGR
                    label = f"{slot_id} - RESERVED"
                else:
                    color = (0, 0, 255)      # Red for occupied
                    label = f"{slot_id} - OCCUPIED"
                
                cv2.polylines(frame, [poly], isClosed=True, color=color, thickness=2)
                
                # Draw slot labels accurately at the centroid
                poly_cx = int(np.mean(poly[:, 0, 0]))
                poly_cy = int(np.mean(poly[:, 0, 1]))
                # Adjust centroid text placement slightly to stay centered
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                text_x = poly_cx - (text_w // 2)
                text_y = poly_cy + (text_h // 2)
                
                cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
            # Draw exit line
            cv2.line(frame, (0, EXIT_LINE_Y), (frame.shape[1], EXIT_LINE_Y), (0, 0, 255), 3)
            cv2.putText(frame, "EXIT LINE", (20, EXIT_LINE_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if latest_results:
                for r in latest_results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        if cls_id in [2, 3, 5, 7] and conf >= 0.4:
                            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                            
                            box_area = (x2 - x1) * (y2 - y1)
                            if box_area >= 2000:
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                
                                # Draw center point for debugging conditionally
                                cx = int((x1 + x2) / 2)
                                cy = int((y1 + y2) / 2)
                                
                                if DEBUG_MODE:
                                    cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
                                
                                # Safely extract class name from global_model safely
                                class_name = global_model.names.get(cls_id, "Vehicle") if global_model else "Vehicle"
                                label = f"{class_name.upper()}"
                                
                                cv2.putText(frame, label, (x1, max(y1 - 10, 10)), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
            latest_frame = frame.copy()
            time.sleep(0.04) # Simulate 25fps real-time playback for the stream

    finally:
        if cap:
            cap.release()
        analysis_status["status"] = "completed"
        analysis_running = False
        logging.info("Video processing completed.")
