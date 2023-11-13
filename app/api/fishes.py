from fastapi import Depends, HTTPException, APIRouter

from typing import Annotated, List
from app.api.utils.fishes import create_event_entry, create_fish_entry

from app.api.utils.fishes import create_event_entry
from app.api.utils.fishes import create_fish_entry

from app.db.db_setup import get_session
from app.db.models.event import Event

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas.events import EventSpec
from app.schemas.fishes import FishSpec
from app.schemas.users import UserDetails

from app.api.users import get_current_active_user

import logging

from datetime import datetime

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.ERROR)  # Set the log level to ERROR (or lower)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/fish")
def create_fish_with_event(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)],
    fishes: List[FishSpec],
    event: EventSpec,
    db: Session = Depends(get_session),
):
    try:
        ev = db.query(Event).filter(
            func.date(Event.date) == datetime.strptime(event.date, '%Y-%m-%d').date(),
            Event.zone == event.zone,
            Event.user_id == current_user.user_id,
            Event.fishing_method == event.fishing_method
        ).first()

        if ev:
            logger.info("Updating existing event: %s", ev.event_id)
            ev.quantity_captured += event.quantity_captured #type: ignore
            ev.quantity_conserved += event.quantity_conserved  # type: ignore
            ev.fishing_duration += event.fishing_duration  # type: ignore
            event_id = ev.event_id
        else:
            logger.info("Creating new event")
            new_event = create_event_entry(event, current_user.user_id, db)
            event_id = new_event.event_id
        
        logger.info("Creating fish entries for event_id: %s", event_id)
        fish_objs = [
            create_fish_entry(fish, db, event_id=event_id, user_id=current_user.user_id)
            for fish in fishes
        ]
        
        db.commit()

        return {"message": "List of fishes successfully saved."}
    except Exception as e:
        logger.error("An error occurred in create_fish_with_event: %s", e)
        db.rollback()
<<<<<<< HEAD
        # Handle the exception appropriately (e.g., return an error response)
        raise HTTPException(status_code=500, detail="Failed to create fish")
=======
        raise HTTPException(status_code=500, detail=str(e))
>>>>>>> origin/1-initial-app-setup
