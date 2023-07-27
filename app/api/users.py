from starlette.responses import RedirectResponse

from app.api.utils.users import authenticate_user, create_access_token, get_current_active_user, get_password_hash

from app.db.models.user import User
from app.db.db_setup import get_session

from sqlalchemy.orm import Session

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

from app.schemas.users import UserDetails, Token, UserCreate


router = APIRouter()
@router.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@router.post("/users/", response_model=UserDetails)
async def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Create a hashed password
    hashed_password = get_password_hash(user_data.password)

    # Create the user object
    user = User(username=user_data.username, password=hashed_password, disabled=user_data.disabled)

    # Add the user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username})


    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserDetails)
async def read_users_me(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)]
):
    return current_user


# @router.get("/", include_in_schema=False)
# async def root():
#     return {"message": "Hello Abenaki"}

# @router.get("/users")
# async def get_users(db : Session = Depends(get_session)):
#     result = db.query(User).all()
#     return result