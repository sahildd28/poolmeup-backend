from fastapi import APIRouter, HTTPException, status,Depends
from config.database_helper import ensure_db
from .auth_helper import authenticate_user,getUserByUsername, insertUser, SignUpForm, LoginForm, User, UserResponse
import psycopg
from psycopg import sql 

router = APIRouter(
    prefix="/auth",          
    tags=["auth"],           
)

@router.post('/signup')
def signUp(signUpForm: SignUpForm):
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")

    user: User = getUserByUsername(signUpForm.user.username)
    
    if(user):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")    

    # Insert the new user

    user : UserResponse = insertUser(signUpForm.user)
    return user 

@router.post('/login')
def login(login_data : LoginForm) -> User:    
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")
    
    user =  authenticate_user(login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    return user