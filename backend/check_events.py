from database import SessionLocal
from models import SystemEvent
import json

db = SessionLocal()
try:
    events = db.query(SystemEvent).order_by(SystemEvent.timestamp.desc()).limit(20).all()
    print("ID | Type | Timestamp | Message")
    print("-" * 60)
    for e in events:
        print(f"{e.id} | {e.event_type} | {e.timestamp} | {e.message}")
finally:
    db.close()
