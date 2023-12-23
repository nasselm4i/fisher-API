from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..db_setup import Base

class Event(Base):
    __tablename__ = "events"

    front_event_id = Column(String)
    event_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    submission_date = Column(DateTime)
    zone = Column(String)
    gps_coordinate = Column(String)
    quantity_conserved = Column(Integer)
    quantity_captured = Column(Integer)
    fishing_duration = Column(Integer)
    fishing_method = Column(String)
    notes = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # user = relationship("User", back_populates="user", uselist=False)
    fish = relationship("Fish", back_populates="event", uselist=True)