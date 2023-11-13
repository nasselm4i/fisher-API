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

from app.schemas.events import EventSpec, GPSZone


from datetime import datetime
import re

router = APIRouter()


@router.get("/events/fish_count_per_zone")
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


@router.get("/events/stats", response_model=Union[List[FishCaughtByWeek], List[FishCaughtByMonth], List[FishCaughtByYear]])
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

from fastapi import HTTPException, status
import re

@router.get("/events/last_n", response_model=List[EventSpec])
async def get_last_n_events(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)], 
    n: int = Query(10, description="Number of last events to be returned (-1 for all events). Excluding 0."),
    session: Session = Depends(get_session)
):
    if n == 0:
        raise HTTPException(status_code=400, detail="Number of events to fetch cannot be 0.")

    query = session.query(Event) \
        .filter(Event.user_id == current_user.user_id) \
        .order_by(Event.date.desc())

    # If n is not -1, we limit the results
    if n != -1:
        query = query.limit(n)

    last_n_events = query.all()

    # Convert the ORM objects to the Pydantic model
    events_details = []
    for event in last_n_events:
        # Convert date to string format
        date_str = event.date.strftime('%Y-%m-%d') if event.date else 'N/A'
    
        # Check if submission_date is None before formatting
        if event.submission_date:
            submitted_date_str = event.submission_date.strftime('%Y-%m-%d')
        else:
            submitted_date_str = 'N/A'
        
        # Parse the gps_coordinate string to extract latitude and longitude
        match = re.match(r"\((.*), (.*)\)", event.gps_coordinate)
        if match:
            latitude, longitude = map(float, match.groups())
        else:
            # Option 1: Provide default values
            latitude, longitude = 0.0, 0.0
            
            # Option 2: Raise an error
            # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            #                     detail="Failed to parse GPS coordinates.")
        
        gps_zone = GPSZone(latitude=latitude, longitude=longitude)
        
        event_spec = EventSpec(
            front_event_id=event.front_event_id,
            submission_date=submitted_date_str,
            date=date_str,
            zone=event.zone,
            gps_coordinate=gps_zone,
            fishing_method=event.fishing_method,
            quantity_captured=event.quantity_captured,
            quantity_conserved=event.quantity_conserved,
            fishing_duration=event.fishing_duration,
            notes=event.notes
        )
        events_details.append(event_spec)

    return events_details
