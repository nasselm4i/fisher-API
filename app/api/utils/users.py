<<<<<<< HEAD
from jose import JWTError, jwt

from app.db.models.user import User
from app.db.db_setup import get_session

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session

from pydantic import ValidationError, SecretStr

=======
import random
from datetime import datetime, timedelta
from typing import Annotated
from pydantic import ValidationError, SecretStr
>>>>>>> origin/1-initial-app-setup
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)
<<<<<<< HEAD


from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated

from app.schemas.users import UserDetails, TokenData

import os


SECRET_KEY = os.environ.get("SECRET_KEY") or "test"
ALGORITHM = os.environ.get("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sqlalchemy_to_dict(obj):
    mapper = class_mapper(obj.__class__)
    return {col.name: getattr(obj, col.name) for col in mapper.column_attrs}
=======
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.db_setup import get_session
from app.schemas.users import UserDetails, TokenData
import os

import smtplib, ssl
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

SECRET_KEY = os.environ.get("SECRET_KEY") or "test"
ALGORITHM = os.environ.get("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def generate_verification_code(length=6):
    return ''.join(random.choice('0123456789') for i in range(length))
>>>>>>> origin/1-initial-app-setup

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
<<<<<<< HEAD
    return current_user
=======
    return current_user

def sqlalchemy_to_dict(obj):
    mapper = class_mapper(obj.__class__)
    return {col.name: getattr(obj, col.name) for col in mapper.column_attrs}
        

def send_verification_email_with_code(email, code):
    # Load the email template
    env = Environment(loader=FileSystemLoader('app/templates'))
    template = env.get_template('verification_email_template.html')

    # Render the email template with the verification code
    html = template.render(code=code)

    # Create the email message
    msg = EmailMessage()
    msg.set_content(html, subtype='html')

    msg['Subject'] = 'Votre code de vérification'
    msg['From'] = 'carnetdupecheurabenaki.dev@gmail.com'
    msg['To'] = email

    # Use gmail to send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login('carnetdupecheurabenaki.dev@gmail.com', 'iyrz bsty wntz jmpe')
        s.send_message(msg)

def send_email_with_template(subject, recipient, template_name, **kwargs):
    # Load the email template
    env = Environment(loader=FileSystemLoader('app/templates'))
    template = env.get_template(template_name)

    # Render the email template with provided keyword arguments
    html = template.render(**kwargs)

    # Create the email message
    msg = EmailMessage()
    msg.set_content(html, subtype='html')

    msg['Subject'] = subject
    msg['From'] = 'carnetdepecheabenaki.dev@gmail.com'
    msg['To'] = recipient

    # Use gmail to send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login('carnetdupecheurabenaki.dev@gmail.com', 'iyrz bsty wntz jmpe')
        s.send_message(msg)
>>>>>>> origin/1-initial-app-setup
