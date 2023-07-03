import fastapi
from typing import Optional, List
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel

router = fastapi.APIRouter()

class Fish(BaseModel):
    fish_id: int
    specie: str
    weight: int
    length: int
    cooking_method: str
    consumed_organs: str
    tag_no: int
    
fishes = []

@router.get("/fishes")
def get_fishes():
    return fishes

@router.get("/fishes/{id}")
def get_fish(
    id: int):
    return {"fish": fishes[id]}

@router.post("/fishes")
def add_fish(fish : Fish):
    fishes.append(fish)
    return {"message": "Fish added."}
