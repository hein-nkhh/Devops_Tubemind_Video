from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SummaryJob(Base):
    __tablename__ = "summary_jobs"
    id = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    status = Column(String, default="processing")
    summary = Column(Text)
    error_message = Column(String(255))
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True)
    job_id = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
