from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user") 

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending") 
    file_path = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"  

    token = Column(String, primary_key=True)  
    blacklisted_at = Column(DateTime, default=datetime.now(timezone.utc))  
    expires_at = Column(DateTime)  

    def is_expired(self):
        return datetime.now(timezone.utc)() > self.expires_at