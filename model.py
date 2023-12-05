from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    full_name: str or None = None
    email: EmailStr or None = None
    disabled: bool or None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None

class UserInDB(User):
    hashed_password: str