from typing import Optional, List
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel


description = """
## Items

You can **read items**.

## Utilisateur

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).

* **Add fish** (_not implemented_).
* **Read fish** (_not implemented_).

* **Add Events** (_not implemented_).
* **Read Events** (_not implemented_).

"""

app = FastAPI(
    title="Carnet du Pêcheur API",
    description=description,
    summary="Everything needed for the development of the Fishing App for Abenakis",
    version="0.0.1",
    contact={
        "name": "Nassim Massaudi",
        "email": "naelm31@ulaval.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

users = []



class User(BaseModel):
    email: str
    is_active: bool


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/users/{id}")
async def get_users():
    return users

@app.get("/users/{id}")
async def get_user(
    id: int = Path(..., description="The ID of the user you want to retrieve", gt=2),
    q: str = Query(None, max_length=5)
    ):
    return {"user": users[id], "query": q} 

@app.post("/users")
async def create_users(user : User):
    users.append(user)
    return {"message": "User created."} 