from fastapi import APIRouter, HTTPException, status
from config.database_helper import ensure_db
from .auth_helper import authenticate_user,getUserByUsername, insertUser, SignUpForm, LoginForm, UserResponse

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

@router.post('/signup')
def signUp(signUpForm: SignUpForm):
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")

    user: UserResponse = getUserByUsername(signUpForm.user.username)
    
    if(user):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")    

    # JWT

    # Insert the new user
    user : UserResponse = insertUser(signUpForm.user) 
    return user 

@router.post('/login')
def login(login_data : LoginForm) -> UserResponse:    
    if ensure_db() is False: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Database not found and unable to re-create")
    
    user =  authenticate_user(login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    
    return user