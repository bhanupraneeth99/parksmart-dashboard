import logging
import os
import asyncio
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, SessionLocal
import models
from models import ProcessingJob
from config import START_TIME
from utils.logging_utils import log_event

# 1. Initialize Services
from services.detection_service import get_detection_service
from services.slot_service import slot_service
from services.tracking_service import tracking_service
from worker import job_manager
from websocket_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    log_event("startup", "[STARTUP] system initializing...")
    
    # 0. Initialize WebSocket Manager Loop
    manager.loop = asyncio.get_running_loop()
    
    # 1. Initialize Database
    models.Base.metadata.create_all(bind=engine)
    log_event("startup", "[STARTUP] database initialized")
    
    # 2. Load and Warm-up Detection Service
    detector = get_detection_service()
    if detector:
        log_event("startup", "[STARTUP] detection service loading...")
        # Dummy inference for warm-up
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        detector.detect(dummy)
        log_event("startup", "[STARTUP] detection service ready (warm-up complete)")
    
    # 3. Refresh Slot Cache
    slot_service.refresh_cache()
    log_event("startup", "[STARTUP] slot cache loaded")
    
    # 4. Resume All Processing Jobs
    db = SessionLocal()
    from worker import DEFAULT_VIDEO
    try:
        jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "processing").all()
        for job in jobs:
            final_path = None
            if job.video_path and os.path.exists(job.video_path):
                final_path = job.video_path
            elif os.path.exists(DEFAULT_VIDEO):
                log_event("startup", f"[STARTUP] job {job.job_id} original video missing, falling back to default")
                final_path = DEFAULT_VIDEO
            
            if final_path:
                log_event("startup", f"[STARTUP] resuming job {job.job_id}")
                job.video_path = final_path # Update to valid path
                job_manager.start_worker(job.id, job.job_id, final_path)
            else:
                log_event("startup", f"[STARTUP] job {job.job_id} failed: all video sources missing", {"level": "error"})
                job.status = "failed"
                job.error_message = "Video file missing on startup recovery (fallback failed)"
        db.commit()
    finally:
        db.close()
    
    log_event("startup", "[STARTUP] system ready")
    yield
    # --- SHUTDOWN ---
    log_event("shutdown", "System shutting down...")

app = FastAPI(title="A Real-Time Intelligent Parking Management System using YOLOv11 and FastAPI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
from routes import slots, booking, admin, upload_video, system, debug
app.include_router(slots.router)
app.include_router(booking.router)
app.include_router(admin.router)
app.include_router(upload_video.router)
app.include_router(system.router)
app.include_router(debug.router)

# --- Serve Frontend (SPA Support) ---
# Ensure this is after all API routes
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist"))

if os.path.exists(DIST_DIR):
    # Mount assets folder for static files
    ASSETS_DIR = os.path.join(DIST_DIR, "assets")
    if os.path.exists(ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If it's an API route or websocket, let it pass (though routers should handle it first)
        if full_path.startswith("api/") or full_path == "ws" or full_path == "video-feed":
            return None # This won't actually happen due to order, but for clarity
        
        # Check if file exists in dist
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve index.html for React Router
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    logging.warning(f"Frontend dist directory not found at {DIST_DIR}. Frontend will not be served.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    log_event("system", "[WS] New connection attempt")
    await manager.connect(websocket)
    log_event("system", f"[WS] Client connected. Total: {len(manager.active_connections)}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log_event("system", f"[WS] Client disconnected. Total: {len(manager.active_connections)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
