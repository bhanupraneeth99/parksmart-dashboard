from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ParkingSlot, Booking
import datetime

router = APIRouter()

@router.post("/book-slot")
def book_slot(data: dict, db: Session = Depends(get_db)):
    # Check if slot is available
    slot = db.query(ParkingSlot).filter(ParkingSlot.id == data.get("slot_id")).first()
    
    if not slot:
        return {"error": "Slot not found"}
        
    if slot.status != "available":
        return {"error": "Slot not available"}
        
    # Book the slot
    now = datetime.datetime.utcnow()
    # Set to 1 minute for quick testing demo
    expiry = now + datetime.timedelta(minutes=1)
    
    new_booking = Booking(
        name=data.get("name"),
        phone=data.get("phone"),
        vehicle_number=data.get("vehicle_number"),
        slot_id=data.get("slot_id"),
        booking_time=now,
        expiry_time=expiry,
        status="active"
    )
    
    db.add(new_booking)
    
    # Change slot status to reserved
    slot.status = "reserved"
    
    db.commit()
    
    return {"message": "Slot booked successfully"}
