from fastapi import Depends, HTTPException, APIRouter

from typing import Annotated

from app.api.utils.fishes import create_event_entry
from app.api.utils.fishes import create_fish_entry

from app.db.db_setup import get_session
from app.db.models.event import Event
from app.db.models.fish import Fish

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas.events import EventSpec
from app.schemas.fishes import FishSpecList, FishSpec
from app.schemas.users import UserDetails

from app.api.users import get_current_active_user

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)  # Set the log level to ERROR (or lower)

router = APIRouter()

# @router.get("/fishes")
# async def get_fishes(db : Session = Depends(get_session)):
#     result = db.query(Fish).all()
#     return result

# @router.post("/fishes/{uid}", response_model=FishSpec)
# async def create_fish_with_event(uid: int, fish: FishSpec, event:EventSpec, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
#     print(current_user.id)
#     # if current_user.id != uid:
#     #     raise HTTPException(status_code=403, detail="Unauthorized access")
#     try:
#         event = db.query(Event).filter(
#             func.date(Event.date) == datetime.now().date(),
#             Event.zone == fish.zone, #type: ignore
#             Event.user_id == uid,
#             Event.fishing_method == fish.fishing_method #type: ignore
#         ).first()

#         if event:
#             fish = create_fish_entry(fish, db, event_id=event.event_id) #type: ignore
#         else:
#             event = create_event_entry(fish.zone, db) #type: ignore
#             fish = create_fish_entry(fish, db, event_id=event.event_id) #type: ignore

#         db.commit()
#         db.refresh(fish)
#         return fish
#     except Exception as e:
#         db.rollback()
#         # Handle the exception appropriately (e.g., return an error response)
#         raise HTTPException(status_code=500, detail="Failed to create fish")

@router.post("/fishes/me/", response_model=FishSpecList)
def create_fish_with_event(current_user: Annotated[UserDetails, Depends(get_current_active_user)], fishes: FishSpecList, event: EventSpec, db: Session = Depends(get_session)):
    try:
        # Try to find an event with the same date, zone, and fishing method
        ev = db.query(Event).filter(
            func.date(Event.date) == event.date.date(),
            Event.zone == event.zone, 
            Event.user_id == current_user.user_id,
            Event.fishing_method == event.fishing_method 
        ).first()

        # If it exists, use its event_id for creating fish entries
        if ev:
            event_id = ev.event_id
        else:
            # If it doesn't exist, create a new event and get its event_id
            new_event = create_event_entry(event, current_user.user_id, db)
            event_id = new_event.event_id

        # Create fish entries with the event_id
        fish_objs = [create_fish_entry(fish, db, event_id=event_id, user_id=current_user.user_id) for fish in fishes.fishlist] #type: ignore

        db.commit()

        fish_spec_list = FishSpecList(fishlist=[FishSpec(specie=fish_obj.specie, weight=fish_obj.weight, length=fish_obj.length, cooking_method=fish_obj.cooking_method, consumed_organs=fish_obj.consumed_organs, tag_no=fish_obj.tag_no) for fish_obj in fish_objs]) #type: ignore

        return fish_spec_list
    except Exception as e:
        logger.error("An error occurred in create_fish_with_event: %s", e)
        db.rollback()
        # Handle the exception appropriately (e.g., return an error response)
        raise HTTPException(status_code=500, detail="Failed to create fish")