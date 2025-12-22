from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid = True), primary_key = True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)
    username = Column(String(100), nullable=False)
    created_at = Column(DateTime, default = datetime.now)

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    file_path = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, index=True)  # chống trùng video
    duration = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)

class VideoSource(Base):
    __tablename__ = "video_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))

    source_type = Column(String(20))  # upload | youtube
    youtube_url = Column(String(255), nullable=True)
    youtube_title = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class TranscriptJob(Base):
    __tablename__ = "transcript_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))

    status = Column(String(20), default="pending")
    whisper_model = Column(String(50))
    language = Column(String(10))

    error_message = Column(String(255), nullable=True)

    started_at = Column(DateTime)
    finished_at = Column(DateTime)


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("transcript_jobs.id"))

    content = Column(Text, nullable=False)  # TEXT thay vì String

    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class SumaryJob(Base):
    __tablename__ = "summary_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_job_id = Column(UUID(as_uuid=True), ForeignKey("transcript_jobs.id"))

    status = Column(String(20), default="pending") # pending, processing, done, failed
    error_message = Column(String(255), nullable=True)

    started_at = Column(DateTime)
    finished_at = Column(DateTime)
