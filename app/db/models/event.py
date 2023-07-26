from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..db_setup import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    zone = Column(String)
    quantity_captured = Column(Integer)
    fishing_duration = Column(Integer)
    fishing_method = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # user = relationship("User", back_populates="user", uselist=False)
    fish = relationship("Fish", back_populates="event", uselist=True)
    