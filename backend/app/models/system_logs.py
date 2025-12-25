from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database.db import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)

    log_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    log_type = Column(String(50), nullable=False, index=True)

    function_name = Column(String(150), nullable=False, index=True)

    time_taken = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
