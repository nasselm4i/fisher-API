from starlette.responses import RedirectResponse

from app.db.models.user import User
from app.db.db_setup import get_session

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session

from pydantic import ValidationError, SecretStr

from fastapi import Depends, APIRouter, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes
)

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated

from app.schemas.users import UserDetails, Token, TokenData, UserCreate

import os

router = APIRouter()
@router.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
# @router.get("/", include_in_schema=False)
# async def root():
#     return {"message": "Hello Abenaki"}

# @router.get("/users")
# async def get_users(db : Session = Depends(get_session)):
#     result = db.query(User).all()
#     return result


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("SECRET_KEY") or "test"
ALGORITHM = os.environ.get("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: SecretStr) -> str:
    return pwd_context.hash(password.get_secret_value())


def get_user_by_username(username: str, db: Session) -> UserDetails:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def authenticate_user(username: str, password: str, db: Session):
    user = get_user_by_username(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Replace this with your own secret key used for token signing
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> UserDetails:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the username from the token
        username: str = str(payload.get("sub"))
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
        user = get_user_by_username(username=token_data.username, db=db)
    except (JWTError, ValidationError):
            raise credentials_exception
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def get_current_active_user(
    current_user: Annotated[UserDetails, Security(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

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

def sqlalchemy_to_dict(obj):
    mapper = class_mapper(obj.__class__)
    return {col.name: getattr(obj, col.name) for col in mapper.column_attrs}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)


    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserDetails)
async def read_users_me(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)]
):
    return current_user

