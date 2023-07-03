import fastapi
from pydantic import BaseModel
from starlette.responses import RedirectResponse

router = fastapi.APIRouter()
@router.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")

class User(BaseModel):
    id: int
    username: str
    password: bool
    
users = []


@router.get("/users")
async def get_users():
    return users

@router.get("/users/{id}")
async def get_user(
    id: int):
    return {"user": users[id]}

@router.post("/users")
async def create_users(user : User):
    users.append(user)
    return {"message": "User created."}

@router.put("/users/{id}")
def update_user(
    id: int,
    user : User):
    users[id] = user
    return {"message": "User updated."}

@router.delete("/users/{id}")
def delete_user(
    id: int):
    users.pop(id)
    return {"message": "User deleted."}
