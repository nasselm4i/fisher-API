from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv


load_dotenv()

url = os.getenv('SQLALCHEMY_DATABASE_URL') or "sqlite:///./sql_app.db"

engine = create_engine(url)


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
    )

Base = declarative_base()

# Dependency
def get_session():
    """
    Returns a session object for database operations.

    Returns:
        Session: A session object for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()