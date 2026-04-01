from pydantic import BaseModel

class User(BaseModel):
    username:str
    password:str

class SignUpForm(BaseModel):
    user:User
    signUpMethod:str

class LoginForm(BaseModel):
    username:str
    password:str | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    password_hash: str | None = None

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str

"""
sub: Subject (user identifier, e.g., user ID rather than username).

exp: Expiration time (short-lived, e.g., 15-30 minutes).

iat: Issued at time.

nbf: Not before (optional, prevents use before a certain time).

iss: Issuer (your app/service name).

aud: Audience (who the token is intended for, e.g., your API).

"""

class TokenData(dict):
    sub: str
    iss: str
    aud: str
    iat: int
    exp: int
