from typing import Optional, List
from pydantic import BaseModel, validator


class FishSpec(BaseModel):
    specie: str
    other_specie: Optional[str] = None
    # event_id: int
    weight: Optional[float] = None
    length: Optional[float] = None
    cooking_method: Optional[str] = None
    consumed_organs: Optional[str] = None
    tag_no: Optional[str] = None

    @validator('tag_no')
    def validate_tag_no(cls, tag_no, values):
        if values.get('specie') == 'Esturgeon' and tag_no is None:
            raise ValueError("tag_no is required for specie 'Esturgeon'")
        return tag_no

class FishSpecList(BaseModel):
    fishlist: List[FishSpec]
        
class FishCaughtByWeek(BaseModel):
    week_number: int
    year_number: int
    fish_type: str
    type_count: int
    
class FishCaughtByMonth(BaseModel):
    month_number: int
    year_number: int
    fish_type: str
    type_count: int

class FishCaughtByYear(BaseModel):
    year_number: int
    fish_type: str
    type_count: int
    
    
class FishCaughtByWeekMerged(BaseModel):
    week_number: int
    year_number: int
    total_count: int
    
class FishCaughtByMonthMerged(BaseModel):
    month_number: int
    year_number: int
    total_count: int

class FishCaughtByYearMerged(BaseModel):
    year_number: int
    total_count: int
