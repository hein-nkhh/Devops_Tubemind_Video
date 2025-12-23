import os
import uuid

from sqlalchemy.orm import Session
from libs.common.database import SessionLocal
from libs.common.models import VideoTask
from libs.common.logger import get_logger
from .core import TranscriberEngine

logger = get_logger("transcriber-worker")


def run():
    engine = TranscriberEngine()
    db: Session = SessionLocal()

    youtube_url = "https://www.youtube.com/watch?v=n8xX8M0U3aY"
    video_id = str(uuid.uuid4())

    raw_audio = None
    mp3_audio = None

    try:
        # Download audio gốc (webm/m4a)
        raw_audio = engine.download_from_youtube(youtube_url, video_id)

        # Convert sang mp3 bằng moviepy
        mp3_audio = engine.convert_to_mp3(raw_audio, video_id)

        # Upload mp3 lên MinIO
        minio_object = engine.upload_audio_to_minio(mp3_audio)

        # Create DB task
        task = VideoTask(
            filename=os.path.basename(mp3_audio),
            minio_object_name=minio_object,
            email="test@local",
            status="processing"
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Transcribe mp3
        transcript = engine.transcribe_file(mp3_audio)

        # Update DB
        task.transcript = transcript
        task.status = "done"
        db.commit()

        logger.info(f"Task completed: task_id={task.id}")

    except Exception as e:
        logger.error(f"Run failed: {e}", exc_info=True)
        db.rollback()

    finally:
        db.close()

        # Cleanup file tạm (khuyên dùng)
        for f in [raw_audio, mp3_audio]:
            if f and os.path.exists(f):
                os.remove(f)
                logger.info(f"Removed temp file: {f}")


if __name__ == "__main__":
    run()
