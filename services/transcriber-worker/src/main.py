from fastapi import FastAPI, UploadFile, BackgroundTasks
from contextlib import asynccontextmanager
from src.config import Config
from logger import logger
from src.database.database import SessionLocal
from src.database.database_models import Video, VideoSource, TranscriptJob, Transcript
import hashlib
import shutil
import os
from datetime import datetime
from sqlalchemy import text
from src.database.database import engine
from src.database.database_models import Base
from fastapi import HTTPException
import whisper
import yt_dlp
import uuid

Base.metadata.create_all(bind=engine)

def get_file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(title=Config.APP_NAME, lifespan=lifespan)


@app.post("/video/upload")
async def upload_video(file: UploadFile):
    logger.info("Received video upload")

    os.makedirs(Config.VIDEO_DIR, exist_ok=True)
    path = os.path.join(Config.VIDEO_DIR, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_hash = get_file_hash(path)
    db = SessionLocal()

    video = db.query(Video).filter_by(file_hash=file_hash).first()
    if video:
        logger.info("Video already exists in DB")
        return {"video_id": str(video.id), "status": "exists"}

    video = Video(file_path=path, file_hash=file_hash)
    db.add(video)
    db.commit()

    logger.info(f"Saved video {video.id}")
    db.refresh(video)
    return {"video_id": str(video.id), "status": "uploaded"}

@app.post("/video/youtube")
def youtube_video(url: str):
    logger.info(f"Received YouTube URL: {url}")

    db = SessionLocal()

    # If this youtube url already exists, return existing video id
    existing_source = db.query(VideoSource).filter_by(youtube_url=url).first()
    if existing_source:
        logger.info(f"YouTube URL already exists in DB for video {existing_source.video_id}")
        db.close()
        return {"status": "exists", "video_id": str(existing_source.video_id)}

    # Create a Video record (use the youtube url as file_path placeholder)
    video = Video(file_path=url)
    db.add(video)
    db.commit()
    db.refresh(video)

    # Create VideoSource linking to the video
    vs = VideoSource(video_id=video.id, source_type="youtube", youtube_url=url)
    db.add(vs)
    db.commit()
    db.refresh(vs)

    logger.info(f"Created video {video.id} and video_source {vs.id} for YouTube URL")
    db.close()
    return {"status": "queued", "video_id": str(video.id)}

def download_youtube_audio(url: str) -> str:
    os.makedirs(Config.VIDEO_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(Config.VIDEO_DIR, filename)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path.replace(".mp3", ".%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path

@app.post("/transcript/{video_id}")
def create_transcript(video_id: str, background_tasks: BackgroundTasks):
    logger.info(f"Create transcript job for video {video_id}")

    db = SessionLocal()
    job = TranscriptJob(
        video_id=video_id,
        status="processing",
        whisper_model=Config.WHISPER_MODEL,
        language=Config.LANGUAGE,
        started_at=datetime.now()
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(run_transcribe, job.id)

    return {"job_id": str(job.id)}

@app.get("/transcript/video/{video_id}")
def get_transcript(video_id: str):
    db = SessionLocal()

    job = (
        db.query(TranscriptJob)
        .filter(TranscriptJob.video_id == video_id)
        .order_by(TranscriptJob.started_at.desc())
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Transcript job not found")

    if job.status != "done":
        return {
            "status": job.status,
            "message": "Transcript not ready yet"
        }

    transcript = (
        db.query(Transcript)
        .filter(Transcript.job_id == job.id)
        .first()
    )

    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not available")

    return {
        "video_id": video_id,
        "job_id": str(job.id),
        "status": job.status,
        "content": transcript.content
    }

def run_transcribe(job_id: str):
    logger.info(f"Start transcribing job {job_id}")
    db = SessionLocal()

    try:
        #  Lấy job
        job = db.query(TranscriptJob).filter(
            TranscriptJob.id == job_id
        ).first()

        if not job:
            logger.error("TranscriptJob not found")
            return

        #  Lấy video
        video = db.query(Video).filter(
            Video.id == job.video_id
        ).first()

        if not video:
            raise Exception("Video not found")

        #  Xác định audio path
        if video.file_path.startswith("http"):
            logger.info("Downloading YouTube audio")
            audio_path = download_youtube_audio(video.file_path)
        else:
            audio_path = video.file_path

        # Load whisper
        model = whisper.load_model(job.whisper_model)

        logger.info(f"Running whisper on {audio_path}")
        result = model.transcribe(
            audio_path,
            language=job.language
        )

        transcript_text = result["text"]

        # Save transcript
        transcript = Transcript(
            job_id=job.id,
            content=transcript_text,
            created_at=datetime.now()
        )
        db.add(transcript)

        # Update job
        job.status = "done"
        job.finished_at = datetime.now()

        db.commit()
        logger.info(f"Finished job {job_id}")

    except Exception as e:
        db.rollback()
        job.status = "failed"

        # ⚠️ tránh lỗi varchar(255)
        job.error_message = str(e)[:250]

        db.commit()
        logger.error(f"Transcribe error: {e}")

    finally:
        db.close()
