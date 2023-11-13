from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from ..db_setup import Base

class ProblemReport(Base):
    __tablename__ = 'problem_report'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    problem_type = Column(String)
    problem = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
class ExoticFishReport(Base):
    __tablename__ = 'exotic_fish_report'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    fish_type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)