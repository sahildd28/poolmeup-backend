import psycopg
from psycopg import sql
from psycopg_pool import ConnectionPool
import os,logging
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url 
import logging
from typing import Optional

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

target_db = os.getenv("TARGET_DB") 

def get_connections(dbname:Optional[str] = None):

    if not dbname:
        dbname = target_db  
    try:
        parsed_url = make_url(DATABASE_URL)
        
    except Exception as e:
        logger.warning('Failed in ensure_db', e )
        return False  

    conn_kwargs = {
        "host": parsed_url.host,
        "port": parsed_url.port,
        "user": parsed_url.username,
        "password": parsed_url.password,
        "dbname": dbname,
    }
    
    return conn_kwargs


def ensure_db()-> bool:

    conn_kwargs = get_connections()  
  
    try:
        with psycopg.connect(**conn_kwargs,autocommit=True) as conn: 
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
                exists = cur.fetchone()
                if exists: return True
                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
                    logger.info("Created session database '%s' for chat history", target_db)
                    return True
    except Exception as exc:
        logger.warning("Unable to auto-create session DB '%s': %s", target_db, exc)
        return False
    
    
