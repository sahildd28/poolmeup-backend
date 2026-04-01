import os
from fastapi import Depends, HTTPException,status
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
import logging
from sqlalchemy import text
from app.config.database_helper import get_connections
from datetime import datetime
from app.model.authModel import User, UserResponse
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

password_hash = PasswordHash.recommended()
hash = password_hash.hash("123")

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token_data(data:OAuth2PasswordRequestForm) -> dict:
    return dict(
        sub=data.username,
        iss='poolmeup_backend',
        aud='poolmeup_api',
        iat = int(datetime.now(timezone.utc).timestamp()),
        exp = int((datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
    )


def create_access_token(data: dict ) -> str :    
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

async def get_current_user(token: str = Depends(oauth_scheme)): 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ) 
    payload_data =  jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={"verify_aud": False})
    
    username: str = payload_data.get("sub")

    if username is None:
        raise credentials_exception
    
    user : UserResponse = getUserByUsername(username)

    if not user:
        raise credentials_exception
    
    return user


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def insertUser(user: User) -> UserResponse:
    try:
        engine = get_connections()
        hashed_password = get_password_hash(user.password)

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO user_details (username, password_hash, create_date, role)
                    VALUES (:username, :password_hash, :create_date, :role)
                    RETURNING id, username
                """),
                {
                    "username": user.username,
                    "password_hash": hashed_password,
                    "create_date" : datetime.now(),
                    "role" : "user"              
                }
            ).fetchone()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Insert failed"
                )

            return UserResponse(
                id=result.id,
                username=result.username
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation didn't succeed: {e}"
        )

def getUserByUsername(username: str) -> UserResponse:

    try:
        engine = get_connections()

        with engine.connect() as conn:
            result =conn.execute( text("""SELECT id, username, password_hash from user_details where username = :username"""),
            {
                "username" : username
            }
            ).fetchone()          
            if result:
                return UserResponse(
                    id=result.id,
                    username=result.username,
                    password_hash=result.password_hash
                )           
          
    except HTTPException as e:
        logging.error('Failed to perform getUserByUsername', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database operation didnt succeed")

    return None


def authenticate_user(loginDetails :OAuth2PasswordRequestForm ) -> UserResponse | None:
    
    user: UserResponse = getUserByUsername(loginDetails.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")

    if not verify_password(loginDetails.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    
    return user
