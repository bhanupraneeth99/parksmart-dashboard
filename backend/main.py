import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
import models
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Routers
from routes import slots, booking, admin, upload_video
from booking_timer import scheduler

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parksmart API")

@app.get("/health")
def health_check():
    from parking_detection import analysis_status, analysis_running
    return {
        "status": "running",
        "analysis": analysis_status.get("status", "idle"),
        "running": analysis_running
    }

@app.get("/analysis-status")
def get_analysis_status():
    from parking_detection import analysis_running
    return {"running": analysis_running}

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routers
app.include_router(slots.router)
app.include_router(booking.router)
app.include_router(admin.router)
app.include_router(upload_video.router)

def initialize_db():
    db = SessionLocal()
    try:
        existing = db.query(models.ParkingSlot).first()
        if not existing:
            default_slots = []
            for i in range(1, 8):
                default_slots.append((f"S{i}", f"S-0{i}", "S"))
                
            for s_id, s_num, s_floor in default_slots:
                new_slot = models.ParkingSlot(
                    id=s_id, number=s_num, floor=s_floor, status="available"
                )
                db.add(new_slot)
            db.commit()
            logging.info("Database initialized with default slots.")
    except Exception as e:
        logging.error(f"Error initializing DB: {e}")
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Automatically seed DB
    initialize_db()
    
    # Start APScheduler
    scheduler.start()
    logging.info("Booking expiry timer started.")

@app.on_event("shutdown")
def shutdown_event():
    try:
        scheduler.shutdown()
        logging.info("Booking expiry timer stopped.")
    except Exception as e:
        logging.error(f"Error stopping timer: {e}")
