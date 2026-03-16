from database import SessionLocal
from models import ProcessingJob, SystemEvent
import os

db = SessionLocal()
try:
    print(f"Current Directory: {os.getcwd()}")
    
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.id.desc()).limit(5).all()
    print("\n--- Latest Jobs ---")
    for j in jobs:
        print(f"ID: {j.id} | JobID: {j.job_id} | Status: {j.status} | CreatedAt: {j.created_at} | Error: {j.error_message}")
    
    events = db.query(SystemEvent).order_by(SystemEvent.id.desc()).limit(15).all()
    print("\n--- Latest Events ---")
    for e in events:
        print(f"[{e.event_type}] ({e.timestamp}) {e.message}")
finally:
    db.close()
