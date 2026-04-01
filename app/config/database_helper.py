
import os,logging
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url 
import logging
from app.entity.auth_entity import Base  
from typing import Optional
from sqlalchemy import create_engine,text

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

target_db = os.getenv("TARGET_DB") 

admin_db = os.getenv("ADMIN_DB")

def get_connections(dbname: Optional[str] = None):
    try:
        url_object = make_url(DATABASE_URL)
        if dbname:
            url_object = url_object.set(database=dbname)

        engine = create_engine(
            url_object,
            isolation_level="AUTOCOMMIT",
            echo=True
        )
        return engine
    
    except Exception as e:
        logger.error("Couldn't create or fetch the database connection: %s", e)
        return None
    

def ensure_db() -> bool:
    print("TARGET_DB", target_db, DATABASE_URL)
    try:
        # Step 1: connect to admin DB
        server_engine = get_connections(admin_db or "postgres")

        with server_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": target_db}
            ).fetchone()

            if not result:
                conn.execute(text(f'CREATE DATABASE "{target_db}"'))
                logger.info("Created database '%s'", target_db)

        server_engine.dispose()

        # Step 2: connect to target DB and create tables
        app_engine = get_connections(target_db)
        Base.metadata.create_all(app_engine)   # creates tables if missing
        app_engine.dispose()

        return True

    except Exception as e:
        logger.error("Failed to create database connection: %s", e)
        return False
   
    
    


