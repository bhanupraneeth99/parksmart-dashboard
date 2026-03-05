from sqlalchemy import Column, String, Integer, DateTime
from database import Base
import datetime

class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(String(50), primary_key=True, index=True)
    number = Column(String(50))
    floor = Column(String(50))
    status = Column(String(50), default="available")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100))
    phone = Column(String(20))
    vehicle_number = Column(String(50))
    slot_id = Column(String(50))
    booking_time = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_time = Column(DateTime)
    status = Column(String(50), default="active")
