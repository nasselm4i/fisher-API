from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DefaultClause

from ..db_setup import Base

target_metadata = Base.metadata

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String)
    disabled = Column(Boolean, server_default=DefaultClause('false'), nullable=False)
    email = Column(String, unique=True, index=True)
    is_email_verified = Column(Boolean, default=False, server_default=DefaultClause('false'), nullable=False)
    email_verification_code = Column(String)
    # user_info = relationship("UserInfo", back_populates="user", uselist=False)
    # fish = relationship("Fish", back_populates="user", uselist=True)
    # event = relationship("Event", back_populates="user", uselist=True)


class UserInfo(Base):
    __tablename__ = "user_info"

    user_info_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    fishing_license_number = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, primary_key=True)
    # user = relationship("User", back_populates="user_info", uselist=False)
    
class Code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)