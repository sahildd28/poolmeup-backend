import os
from pydantic import BaseModel
from fastapi import HTTPException,status
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordRequestForm 
import logging
from sqlalchemy import text
from config.database_helper import get_connections
from datetime import datetime

SECRET_KEY = os.getenv('SECRET_KEY')
ALGOTIRHM = os.getenv('ALGOTIRHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

password_hash = PasswordHash.recommended()
hash = password_hash.hash("123")

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
                    INSERT INTO user_details (username, password_hash, create_date)
                    VALUES (:username, :password_hash, :create_date)
                    RETURNING id, username
                """),
                {
                    "username": user.username,
                    "password_hash": hashed_password,
                    "create_date" : datetime.now()               
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
            result =conn.execute( text("""SELECT id, username from user_details where username = :username"""),
            {
                "username" : username
            }
            ).fetchone()

            if result:
                return UserResponse(
                    id=result.id,
                    username=result.username
                )           
          
    except HTTPException as e:
        logging.error('Failed to perform getUserByUsername', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database operation didnt succeed")

    return None


def authenticate_user(loginDetails :OAuth2PasswordRequestForm ) -> UserResponse | None:
    return getUserByUsername(loginDetails.username)