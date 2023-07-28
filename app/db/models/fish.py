from sqlalchemy import Column, Integer, String,  ForeignKey
from sqlalchemy.orm import relationship

from ..db_setup import Base

class Fish(Base):
    __tablename__ = "fishes"

    fish_id = Column(Integer, primary_key=True, index=True)
    specie = Column(String)
    weight = Column(Integer)
    length = Column(Integer)
    cooking_method = Column(String)
    consumed_organs = Column(String)
    tag_no = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    # user = relationship("User", back_populates="fish", uselist=False) 
    event = relationship("Event", back_populates="fish", uselist=False)
    