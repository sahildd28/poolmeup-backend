import os
from pydantic import BaseModel
from fastapi import HTTPException,status
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordRequestForm 
import psycopg
from psycopg import sql
from config.database_helper import get_connections

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

    conn_kwargs = get_connections()
    hashed_password = get_password_hash(user.password)

    try:
        with psycopg.connect(**conn_kwargs,autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO user_details (username, password_hash) VALUES (%s, %s) RETURNING id,username",(user.username, hashed_password) )
                
                row = cur.fetchone()
                columns = [desc[0] for desc in cur.description]  # extract column names
                user_detail = dict(zip(columns, row))            # map names to values

                print ('herer',user_detail)

                return UserResponse(
                    id= user_detail["id"],username = user_detail["username"],      
                )
                
                         
                
                
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database operation didnt succeed")

    return None

def getUserByUsername(username: str):

    conn_kwargs = get_connections()

    try:
        with psycopg.connect(**conn_kwargs,autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM user_details WHERE username = %s",(username,))
                record = cur.fetchone()
                if record : 
                    return record
                
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database operation didnt succeed")

    return None


def authenticate_user(loginDetails :OAuth2PasswordRequestForm ) -> User | None:
    return getUserByUsername(loginDetails.username)