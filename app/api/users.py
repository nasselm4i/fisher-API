
from secrets import token_urlsafe

from pydantic import SecretStr
from app.db.models.user import User
from app.db.db_setup import get_session

from sqlalchemy.orm import Session


from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from passlib.context import CryptContext
from datetime import timedelta
from typing import Annotated

from app.schemas.users import UserDetails, Token, UserCreate

import os


from app.api.utils.users import get_current_active_user, get_password_hash, authenticate_user, create_access_token, generate_verification_code, send_email_with_template, send_verification_email_with_code

from fastapi import Body

from app.db.models.report import ExoticFishReport, ProblemReport


router = APIRouter()
# @router.get("/", include_in_schema=False)
# async def docs_redirect():
#     return RedirectResponse(url="/docs")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.environ.get("SECRET_KEY") or "test"
ALGORITHM = os.environ.get("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 99999999

@router.post("/registration", response_model=Token)
async def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create a hashed password
    hashed_password = get_password_hash(user_data.password)

    # Create the user object
    user = User(username=user_data.username, password=hashed_password, email=user_data.email,  disabled=False)
    verification_code = generate_verification_code()
    user.email_verification_code = verification_code  # type: ignore
    db.add(user)
    db.commit()
    send_verification_email_with_code(user.email, verification_code)

    db.refresh(user)

    # After registering the user, generate an access token for them
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username
    }

@router.post("/submit-verification-code")
async def submit_verification_code(email: str = Body(...), code: str = Body(...), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if user.is_email_verified: # type: ignore
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

    if user.email_verification_code != code: # type: ignore
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    if user.email_verification_code == code: # type: ignore
        user.is_email_verified = True # type: ignore
        db.commit()
        return {"message": "Email successfully verified."}
    return {"message": "An Error as occured."}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Incorrect username or password", 
                            headers={"WWW-Authenticate": "Bearer"})
    # if not user.is_email_verified:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail="Email not verified", 
    #                         headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username
    }


@router.get("/user", response_model=UserDetails)
async def read_users_me(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)]
):
    return current_user


@router.post("/lost-password")
async def lost_password(email: str = Body(... , embed=True), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    
    # Generate a new random password
    new_password = token_urlsafe(8)
    new_password_secret = SecretStr(new_password)
    
    # Hash the new password
    hashed_password = get_password_hash(new_password_secret)
    
    # Update the user's password in the database
    user.password = hashed_password # type: ignore
    db.commit()

    # Send the new password to the user's email using the new template
    send_email_with_template(
        subject="Informations de Connexion",
        recipient=email,
        template_name='reset_password_template.html',
        username=user.username,
        password=new_password
    )

    return {"message": "A new password has been sent to your email."}


@router.post("/report-problem")
async def report_problem(username: str = Body(... , embed=True), problem: str = Body(... , embed=True), problem_type: str = Body(... , embed=True), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not registered")
    
    # Create the problem report object
    problem_report = ProblemReport(username=username, problem=problem, problem_type=problem_type)
    db.add(problem_report)
    db.commit()

    db.refresh(problem_report)

    return {"message": "Problem has been submitted successfully."}

@router.post("/report-exotic-fish")
async def report_exotic_fish(username: str = Body(... , embed=True), fish_type: str = Body(... , embed=True), db:
    Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not registered")

    # Create the problem report object
    exotic_fish_report = ExoticFishReport(username=username, fish_type=fish_type)
    db.add(exotic_fish_report)
    db.commit()

    db.refresh(exotic_fish_report)

    return {"message": "Exotic Fish has been submitted successfully."}

@router.post("/change-password")
async def change_password(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)],
    old_password: str = Body(... , embed=True),
    new_password: str = Body(... , embed=True),
    db: Session = Depends(get_session)
):
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not pwd_context.verify(old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    # Hash the new password
    hashed_password = get_password_hash(SecretStr(new_password))
    
    # Update the user's password in the database
    user.password = hashed_password # type: ignore
    db.commit()
    
    return {"message": "Password successfully changed."}

@router.post("/lost-password")
async def lost_password(email: str = Body(... , embed=True), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    
    # Generate a new random password
    new_password = token_urlsafe(8)
    new_password_secret = SecretStr(new_password)
    
    # Hash the new password
    hashed_password = get_password_hash(new_password_secret)
    
    # Update the user's password in the database
    user.password = hashed_password # type: ignore
    db.commit()

    # Send the new password to the user's email using the new template
    send_email_with_template(
        subject="Informations de Connexion",
        recipient=email,
        template_name='reset_password_template.html',
        username=user.username,
        password=new_password
    )

    return {"message": "A new password has been sent to your email."}


@router.post("/report-problem")
async def report_problem(username: str = Body(... , embed=True), problem: str = Body(... , embed=True), problem_type: str = Body(... , embed=True), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not registered")
    
    # Create the problem report object
    problem_report = ProblemReport(username=username, problem=problem, problem_type=problem_type)
    db.add(problem_report)
    db.commit()

    db.refresh(problem_report)

    return {"message": "Problem has been submitted successfully."}

@router.post("/report-exotic-fish")
async def report_exotic_fish(username: str = Body(... , embed=True), fish_type: str = Body(... , embed=True), db:
    Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not registered")

    # Create the problem report object
    exotic_fish_report = ExoticFishReport(username=username, fish_type=fish_type)
    db.add(exotic_fish_report)
    db.commit()

    db.refresh(exotic_fish_report)

    return {"message": "Exotic Fish has been submitted successfully."}

@router.post("/change-password")
async def change_password(
    current_user: Annotated[UserDetails, Depends(get_current_active_user)],
    old_password: str = Body(... , embed=True),
    new_password: str = Body(... , embed=True),
    db: Session = Depends(get_session)
):
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not pwd_context.verify(old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    # Hash the new password
    hashed_password = get_password_hash(SecretStr(new_password))
    
    # Update the user's password in the database
    user.password = hashed_password # type: ignore
    db.commit()
    
    return {"message": "Password successfully changed."}

# @router.get("/", include_in_schema=False)
# async def root():
#     return {"message": "Hello Abenaki"}

# @router.get("/users")
# async def get_users(db : Session = Depends(get_session)):
#     result = db.query(User).all()
#     return result