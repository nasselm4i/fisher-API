from datetime import datetime

from app.db.models.event import Event
from app.db.models.fish import Fish

from app.schemas.events import EventSpec
from app.schemas.fishes import FishSpec

from sqlalchemy.orm import Session


# fish_codes_dict = {
#     "Achigan (petite ou grande bouche)": "AC",
#     "Barbotte": "BA",
#     "Barbue": "BA",
#     "Brochet": "BR",
#     "Maskinongé": "BR",
#     "Doré jaune": "DR",
#     "Doré noir": "DR",
#     "Esturgeon": "ES",
#     "Omble de fontaine (Truite mouchetée)": "OF",
#     "Ouananiche": "OU",
#     "Perchaude": "PE",
#     "Touladi (truite grise)": "TO",
#     "Anguille": "XP",
#     "Autres espèces": "XP"
# }

fish_codes_dict = {
    "Achigan": "AC",
    "Barbote (Barbue)": "BA",
    "Maskinongé (Brochet)": "BR",
    "Doré": "DR",
    "Esturgeon": "ES",
    "Omble de fontaine": "OF",
    "Ouananiche": "OU",
    "Perchaude": "PE",
    "Touladi (Truite Grise)": "TO",
    "Anguille": "XP", # Can possibly change (ask biologist)
    "Carpe": "XP", # Can possibly change (ask biologist)
    "Autre": "XP"
}

def create_fish_entry(fish: FishSpec, db: Session, event_id: int, user_id: int) -> Fish:
    fish_data = fish.dict()
    specie = fish_data.get('specie')

    # Set fish code based on specie
    fish_code = fish_codes_dict.get(specie, 'XP') if specie else 'XP'  # Default to 'XP' if specie not found
    fish_data['fish_code'] = fish_code

    fish_obj = Fish(**fish_data, event_id=event_id, user_id=user_id)
    db.add(fish_obj)
    return fish_obj

def create_event_entry(event: EventSpec, uid: int, db: Session) -> Event:
    event_obj = Event(
        front_event_id=event.front_event_id,
        date=datetime.strptime(event.date, '%Y-%m-%d'),
        zone=event.zone,
        gps_coordinate='({}, {})'.format(event.gps_coordinate.latitude, event.gps_coordinate.longitude),
        fishing_method=event.fishing_method,
        quantity_captured=event.quantity_captured,
        quantity_conserved=event.quantity_conserved,
        fishing_duration=event.fishing_duration,
        notes=event.notes,
        user_id=uid,
    )
    db.add(event_obj)
    db.commit()
    db.refresh(event_obj)
    return event_obj

# Esturgeon, Perchaude, Maskinongé, Anguille, Brochet, Doré jaune, Doré noir, Barbue, Barbotte, Achigan sp., Autres espèces 
# fish_types = {
#     "AC": "Achigan (petite ou grande bouche)",
#     "BA": "Barbotte ou barbue",
#     "BR": "Brochet ou maskinongé",
#     "DR": "Doré (noir ou jaune)",
#     "ES": "Esturgeon (noir ou jaune)",
#     "OF": "Omble de fontaine (truite mouchetée)",
#     "OU": "Ouananiche",
#     "PE": "Perchaude",
#     "TO": "Touladi (truite grise)",
#     "XP": "Autre espèce poisson"
# }