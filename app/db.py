#database engine helper

import os #reads config (like database URL) from environment variables
from dotenv import load_dotenv #imports helper that reads .env file
from sqlalchemy import create_engine #imprts ftn that create database engine
from sqlalchemy.orm import sessionmaker #builds "template" so I can open a new session whenver I communicate to DB

load_dotenv() #reads .env file and loads values into environment
#this is so os.getenv("DB_URL") actually finds the value set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db") #grabs DB_URL from environment, if missing, uses SQLite file app.db in proj root
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args) #creates the engine

from contextlib import contextmanager
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
#creates a factory, whenever I need to talk to the DB, call SessionLocal()
#autoflush: prevents suprise writes mid-query, autocommit: I decide when to save, EOC: objs stay usable after commit
def get_raw_session():
    return SessionLocal()

@contextmanager #turns ftn into something I can use with "with"
def get_session(): #helper I'll call
    s = SessionLocal() #opens a new DB session 
    try:
        yield s #hands value to the "with" block
        #splits setup and teardown 
        s.commit() #tells DB to save changes
        #any changes made inside the "with" block becomes permanent in the DB
        #only commit if "with" block finished without errors (whye line is placed after yield)
    except Exception:
        s.rollback() #reverts current transaction to state before "with" block started making changes
        #cancles any writes that were about to be committed
        raise #propagates error upward to get traceback in console/logs
    finally: #always rns whether error or not
        s.close() #closes DB

# --- bootstrap: create tables if missing ---
def init_db():
    # Ensure all models are registered before create_all()
    from app.models import Base
    Base.metadata.create_all(bind=engine)

