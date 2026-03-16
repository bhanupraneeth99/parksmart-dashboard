from database import SessionLocal
from models import ProcessingJob

db = SessionLocal()
try:
    job = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).first()
    if job:
        print(f"Job ID: {job.job_id}")
        print(f"Status: {job.status}")
        print(f"Error: {job.error_message}")
        print(f"Created at: {job.created_at}")
    else:
        print("No jobs found.")
finally:
    db.close()
