from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


load_dotenv()

url = os.getenv('SQLALCHEMY_DATABASE_URL')

engine = create_engine( url, connect_args={"check_same_thread": False, future=True} ) # type: ignore 

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
    )

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

