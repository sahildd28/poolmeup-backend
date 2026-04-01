from fastapi import APIRouter, HTTPException, status, Depends
from app.config.database_helper import ensure_db
from app.auth.auth_helper import authenticate_user,getUserByUsername, insertUser, create_token_data, create_access_token, get_current_user
from app.model.authModel import SignUpForm, UserResponse,UserLoginResponse,TokenData
from fastapi.security import OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv

"""
For serverless architecture we can use 
# engine = get_connections()
# engine.dispose()
at end of our routes
"""
router = APIRouter(
    prefix="/auth",          
    tags=["auth"],           
)

load_dotenv()


# Methods


#  Un-Authenticated Routes

@router.post('/signup')
def signUp(signUpForm: SignUpForm):
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")

    user: UserResponse = getUserByUsername(signUpForm.user.username)
    
    if(user):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")    

    # Insert the new user
    user : UserResponse = insertUser(signUpForm.user) 
    return user 

@router.post('/login')
def login(login_data : OAuth2PasswordRequestForm = Depends()) -> UserLoginResponse:    
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")
    
    user =  authenticate_user(login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    
    # Create JWT token
    access_token_data : TokenData = create_token_data(login_data)
    access_token = create_access_token(access_token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(id=user.id, username=user.username)
    }

# Authenticated Routes

@router.get('/user/me')
def get_user_details(current_user: UserResponse = Depends(get_current_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]     