# from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator

class GPSZone(BaseModel):
    latitude: float
    longitude: float

class EventSpec(BaseModel):
    front_event_id: Optional[str] = None
    submission_date: str
    date: str
    zone: str
    gps_coordinate: GPSZone
    fishing_method: str
    quantity_captured: int
    quantity_conserved : int
    fishing_duration: int
    notes : str
    
class EventCaughtWeek(BaseModel):
    week_number: int
    year_number: int
    fish_type: str
    type_count: int
    
class FishCountPerZone(BaseModel):
    zone: str
    fish_count: int

