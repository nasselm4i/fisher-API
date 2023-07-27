from sqlalchemy.orm import Session
from app.db.models.event import Event
from app.db.models.fish import Fish
from app.schemas.events import EventSpec
from app.schemas.fishes import FishSpec


def create_fish_entry(fish: FishSpec, db: Session, event_id: int, user_id: int) -> Fish:
    fish_obj = Fish(**fish.dict(), event_id=event_id, user_id=user_id)
    db.add(fish_obj)
    return fish_obj

def create_event_entry(event: EventSpec, uid: int, db: Session) -> Event:
    event_obj = Event(
        date=event.date,
        zone=event.zone,
        fishing_method=event.fishing_method,
        quantity_captured=event.quantity_captured,
        fishing_duration=event.fishing_duration,
        user_id=uid,
    )
    db.add(event_obj)
    db.commit()
    db.refresh(event_obj)
    return event_obj