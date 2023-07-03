import fastapi
# from typing import Optional, List
# from fastapi import FastAPI, Path, Query
from pydantic import BaseModel
from datetime import datetime

router = fastapi.APIRouter()

class Event(BaseModel):
    event_id: int
    id: int
    date: datetime
    zone: str
    quantity_captured: int
    fishing_duration: int
    
events = []
    
@router.get("/events")
def get_events():
    return events

@router.get("/events/{id}")
def get_event(
    id: int):
    return {"event": events[id]}

@router.post("/events")
def add_event(event : Event):
    events.append(event)
    return {"message": "Event added."}

