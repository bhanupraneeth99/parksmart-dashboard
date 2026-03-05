from fastapi import APIRouter, UploadFile, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import uuid
import os
import shutil
from sqlalchemy.orm import Session
from database import get_db
from models import ParkingSlot
from parking_detection import process_video, analysis_status, get_video_stream, set_analysis_paused

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-parking-video")
def upload_video(file: UploadFile, background_tasks: BackgroundTasks):
    from parking_detection import analysis_running
    
    if analysis_running:
        return {"message": "Analysis already running"}
        
    # Fixed path for overwriting
    path = os.path.join(UPLOAD_DIR, "parking_video.mp4")
    
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    background_tasks.add_task(process_video, path)
    
    return {"message": "Video uploaded. Analysis started."}

@router.get("/analysis-status")
def get_analysis_status():
    from parking_detection import analysis_running
    return {"running": analysis_running}

@router.get("/video-feed")
def video_feed():
    return StreamingResponse(get_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/start-analysis")
def start_analysis():
    set_analysis_paused(False)
    return {"message": "Analysis started"}

@router.post("/stop-analysis")
def stop_analysis():
    set_analysis_paused(True)
    return {"message": "Analysis stopped"}

@router.post("/reset-slots")
def reset_slots(db: Session = Depends(get_db)):
    slots = db.query(ParkingSlot).all()
    for s in slots:
        s.status = "available"
    db.commit()
    return {"message": "Slots reset to available"}

@router.get("/slot-stats")
def slot_stats(db: Session = Depends(get_db)):
    total = db.query(ParkingSlot).count()
    available = db.query(ParkingSlot).filter(ParkingSlot.status == "available").count()
    occupied = db.query(ParkingSlot).filter(ParkingSlot.status == "occupied").count()
    reserved = db.query(ParkingSlot).filter(ParkingSlot.status == "reserved").count()
    return {
        "total_slots": total,
        "available": available,
        "occupied": occupied,
        "reserved": reserved
    }
