import os
from fastapi import FastAPI
from auth.auth_routes import router as auth_router
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database_helper import ensure_db

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

