from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from ..db_setup import Base

class Fish(Base):
    __tablename__ = "fishes"

    id = Column(Integer, primary_key=True, index=True)
    specie = Column(String)
    weight = Column(Integer)
    length = Column(Integer)
    cooking_method = Column(String)
    consumed_organs = Column(String)
    tag_no = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="fish")