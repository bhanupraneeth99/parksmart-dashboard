from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ParkingSlot

router = APIRouter()

@router.get("/slots")
def get_slots(db: Session = Depends(get_db)):
    slots = db.query(ParkingSlot).all()
    
    return [
        {
            "id": s.id,
            "number": s.number,
            "floor": s.floor,
            "status": s.status
        }
        for s in slots
    ]
