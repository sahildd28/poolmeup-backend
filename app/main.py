import os
from fastapi import Depends, FastAPI, HTTPException,status
from app.auth.auth_routes import router as auth_router
from app.auth.auth_helper import authenticate_user, create_token_data, create_access_token
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model.authModel import TokenData,Token
from app.config.database_helper import ensure_db
from fastapi.security import OAuth2PasswordRequestForm

load_dotenv()
app = FastAPI(title="poolmeup_backend")
app.include_router(auth_router)

ensure_db()

DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
                          
@app.get('/') 
def hello():
    return 'Hello' 

# Auth route to get access token for restricted endpoints
@app.post('/token')
def token_helper(login_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user =  authenticate_user(login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    token_data : TokenData = create_token_data(login_data)
    access_token = create_access_token(token_data)
    return Token(access_token=access_token, token_type="bearer")
