from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Booking
import pandas as pd

router = APIRouter()

@router.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings

@router.get("/export")
def export_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    
    data = []
    for b in bookings:
        data.append({
            "ID": b.id,
            "Name": b.name,
            "Phone": b.phone,
            "Vehicle Number": b.vehicle_number,
            "Slot ID": b.slot_id,
            "Booking Time": b.booking_time.strftime("%Y-%m-%d %H:%M:%S") if b.booking_time else None,
            "Expiry Time": b.expiry_time.strftime("%Y-%m-%d %H:%M:%S") if b.expiry_time else None,
            "Status": b.status
        })
        
    df = pd.DataFrame(data)
    filename = "bookings.xlsx"
    df.to_excel(filename, index=False)
    
    return FileResponse(
        path=filename,
        filename="parking_bookings.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
