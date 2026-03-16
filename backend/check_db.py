from database import SessionLocal
from models import ProcessingJob
import os

db = SessionLocal()
try:
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).limit(10).all()
    print("ID | JobID | Path | Status")
    print("-" * 40)
    for j in jobs:
        exists = os.path.exists(j.video_path) if j.video_path else False
        print(f"{j.id} | {j.job_id} | {j.video_path} (Exists: {exists}) | {j.status}")
finally:
    db.close()
