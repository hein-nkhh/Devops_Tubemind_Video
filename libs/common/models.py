from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VideoTask(Base):
    __tablename__ = "video_tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    minio_object_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, default="pending")
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())