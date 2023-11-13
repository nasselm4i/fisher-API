from pydantic import BaseModel, SecretStr, EmailStr, constr

class UserDetails(BaseModel):
    user_id: int
    username: str
    password: SecretStr
    is_email_verified: bool
    disabled: bool | None = None
    
    class Config:
        orm_mode = True
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

class TokenData(BaseModel):
    username: str
    scopes: list[str] = [] 

class UserInDB(UserDetails):
    hashed_password: SecretStr
    
class UserCreate(BaseModel):
    username: constr(min_length=2, max_length=50)  # type: ignore # constrains the string to be at least 1 character long
    password: SecretStr
    email: EmailStr  # validates the email format
    registration_code: str
    # disabled: bool | None = None