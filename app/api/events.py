from fastapi import Depends, APIRouter, Query, HTTPException

from typing import List, Union, Annotated

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.event import Event
from app.db.models.fish import Fish
from app.db.db_setup import get_session

from app.schemas.events import FishCountPerZone
from app.schemas.fishes import FishCaughtByWeek, FishCaughtByMonth, FishCaughtByYear
from app.schemas.users import UserDetails

from app.api.users import get_current_active_user


router = APIRouter()


    
# events = []

# @router.get("/events")
# def get_events():
#     return events

# @router.get("/events/{id}")
# def get_event(
#     id: int):
#     return {"event": events[id]}

# @router.post("/events")
# def add_event(event : EventDetails):
#     events.append(event)
#     return {"message": "Event added."}

# @router.post("/events/{uid}", response_model=EventSpec)
# async def create_event(uid: int, event: EventSpec, db: Session = Depends(get_session)):
#     new_event = Event(
#         date=event.date,
#         zone=event.zone,
#         fishing_method=event.fishing_method,
#         quantity_captured=event.quantity_captured,
#         fishing_duration=event.fishing_duration,
#         user_id=current_user.id
#     )
#     db.add(new_event)
#     db.commit()
#     db.refresh(new_event)
#     return new_event

@router.get("/events/me/fish_count_per_zone/")
async def get_fish_count_per_zone(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)], 
    time_interval: str = Query(..., description="Time interval: week, month, or year"),
    session: Session = Depends(get_session)
):
    # Determine the column and the period to extract based on the time_interval parameter
    if time_interval == "week":
        period_column = func.extract('week', Event.date)
        period_alias = 'week_number'
    elif time_interval == "month":
        period_column = func.extract('month', Event.date)
        period_alias = 'month_number'
    elif time_interval == "year":
        period_column = func.extract('year', Event.date)
        period_alias = 'year_number'
    else:
        raise ValueError("Invalid time interval. Please specify 'week', 'month', or 'year'.")

    # Retrieve the most recent period within the specified time interval
    subquery = session.query(func.max(period_column).label(period_alias)) \
        .filter(Event.user_id == current_user.user_id) \
        .group_by(period_column) \
        .subquery()

    # Count the fish caught per zone for the most recent period within the specified time interval
    query = session.query(
        Event.zone.label('zone'),
        func.count().label('fish_count')
    ).join(Fish, Event.event_id == Fish.event_id) \
        .filter(Event.user_id == current_user.user_id) \
        .filter(period_column == subquery.c[period_alias]) \
        .group_by(Event.zone)

    result = query.all()

    # Format the result using the FishCountPerZone model
    fish_count_per_zone = [
        FishCountPerZone(zone=row.zone, fish_count=row.fish_count)
        for row in result
    ]

    return fish_count_per_zone


@router.get("/events/me/stats/", response_model=Union[List[FishCaughtByWeek], List[FishCaughtByMonth], List[FishCaughtByYear]])
async def get_fish_caught_by_time_range(current_user: Annotated[UserDetails, Depends(get_current_active_user)], time_range: str = Query(...), session: Session = Depends(get_session)):
    query = session.query(
        func.extract('week', Event.date).label('week_number'),
        func.extract('month', Event.date).label('month_number'),
        func.extract('year', Event.date).label('year_number'),
        Fish.specie.label('fish_type'),
        func.count().label('type_count')
    ).join(Fish, Event.user_id == Fish.user_id)\
    .filter(Event.user_id == current_user.user_id)

    if time_range == "weekly":
        query = query.group_by('week_number', 'month_number', 'year_number', Fish.specie)\
            .order_by('year_number', 'month_number', 'week_number')
        result = query.all()
        fish_caught_by_time_range = [
            FishCaughtByWeek(
                week_number=row.week_number,
                year_number=row.year_number,
                fish_type=row.fish_type,
                type_count=row.type_count
            )
            for row in result
        ]
    elif time_range == "monthly":
        query = session.query(
        func.extract('month', Event.date).label('month_number'),
        func.extract('year', Event.date).label('year_number'),
        Fish.specie.label('fish_type'),
        func.count().label('type_count')
    ).join(Fish, Event.user_id == Fish.user_id)\
    .filter(Event.user_id == current_user.user_id)
        query = query.group_by('month_number', 'year_number',  Fish.specie)\
            .order_by('year_number', 'month_number')
        result = query.all()
        fish_caught_by_time_range = [
            FishCaughtByMonth(
                month_number=row.month_number,
                year_number=row.year_number,
                fish_type=row.fish_type,
                type_count=row.type_count
            )
            for row in result
        ]
    elif time_range == "yearly":
        query = session.query(
        func.extract('year', Event.date).label('year_number'),
        Fish.specie.label('fish_type'),
        func.count().label('type_count')
    ).join(Fish, Event.user_id == Fish.user_id)\
    .filter(Event.user_id == current_user.user_id)
        query = query.group_by('year_number', Fish.specie)\
            .order_by('year_number')
        result = query.all()
        fish_caught_by_time_range = [
            FishCaughtByYear(
                year_number=row.year_number,
                fish_type=row.fish_type,
                type_count=row.type_count
            )
            for row in result
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid time range")

    return fish_caught_by_time_range