import os
from fastapi import FastAPI
from auth.auth_routes import router as auth_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="poolmeup_backend")
app.include_router(auth_router)
                   

@app.get('/')
def hello():
    return 'Hello'

