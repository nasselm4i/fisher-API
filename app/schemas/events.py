from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator


class EventSpec(BaseModel):
    date: datetime
    zone: str
    fishing_method: str
    quantity_captured: int
    fishing_duration: int
    
class EventCaughtWeek(BaseModel):
    week_number: int
    year_number: int
    fish_type: str
    type_count: int
    
class FishCountPerZone(BaseModel):
    zone: str
    fish_count: int