from pydantic import BaseModel, SecretStr

class UserDetails(BaseModel):
    user_id: int
    username: str
    password: SecretStr
    disabled: bool | None = None
    
    class Config:
        orm_mode = True
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    scopes: list[str] = [] 

class UserInDB(UserDetails):
    hashed_password: SecretStr
    
class UserCreate(BaseModel):
    username: str
    password: SecretStr
    disabled: bool | None = None