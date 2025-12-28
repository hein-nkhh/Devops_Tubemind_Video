import sys
import os
import json
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)
sys.path.append("/app")

from sqlalchemy.orm import Session
from libs.common.database import SessionLocal
from libs.common.models import VideoTask
from libs.common.logger import get_logger
from libs.common.redis_client import redis_client
from libs.common.constants import (
    QUEUE_TRANSCRIBE, 
    QUEUE_SUMMARIZE, 
    STATUS_PROCESSING, 
    STATUS_COMPLETED, 
    STATUS_FAILED,
    STATUS_TRANSCRIBING,
    STATUS_TRANSCRIPTION_DONE,
    QUEUE_NOTIFIER
)

# from core import TranscriberEngine # run local
from src.core import TranscriberEngine # run in docker

logger = get_logger("transcriber-worker")

def process_task(engine: TranscriberEngine, task_payload: dict):
    db: Session = SessionLocal()
    local_file_path = None
    
    task_id = task_payload.get("id")
    current_minio_object = task_payload.get("object_minio_name")

    logger.info(f"Processing Task ID: {task_id}")

    try:
        task_record = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if not task_record:
            logger.error(f"Task ID {task_id} not found in DB")
            return

        # 1. Update status -> processing
        task_record.status = STATUS_TRANSCRIBING
        db.commit()

        # 2. Phân loại và lấy file về Local
        if current_minio_object.startswith("links/"):
            # === CASE LINK: Tải từ YT -> Upload lại MinIO -> Transcribe ===
            logger.info("Detected Link Task: Downloading from Youtube...")
            
            # a. Đọc URL từ file text trong MinIO
            youtube_url = engine.read_url_from_minio_text(current_minio_object)
            
            # b. Download video/audio từ Youtube về Local
            local_file_path = engine.download_from_youtube(youtube_url)
            
            # c. NEW: Upload file vừa down lên MinIO (folder download_video)
            new_object_name = engine.upload_file_to_minio(local_file_path, "download_video")
            
            # d. Cập nhật DB: trỏ minio_object_name sang file thực tế thay vì file text link
            task_record.minio_object_name = new_object_name
            db.commit()
            logger.info(f"Updated DB minio_object_name to: {new_object_name}")

        else:
            # === CASE UPLOAD: Tải file có sẵn từ MinIO về ===
            logger.info("Detected Video File Task: Downloading from MinIO...")
            local_file_path = engine.download_file_from_minio(current_minio_object)

        # 3. Transcribe (Xử lý file local đang có)
        transcript_text = engine.transcribe_file(local_file_path)

        # 4. Update DB -> completed
        task_record.transcript = transcript_text
        task_record.status = STATUS_TRANSCRIPTION_DONE
        db.commit()
        logger.info(f"Transcription finished for Task {task_id}")

        # 5. Push notify message
        notifier_payload = {
            "id": task_id,
            "service": "transcriber",
            "email": task_record.email,
            "status": task_record.status,
            "object_minio_name": task_record.minio_object_name
        }

        redis_client.push_task(QUEUE_NOTIFIER, notifier_payload)
        logger.info(f"Pushed notification to {QUEUE_NOTIFIER}: {notifier_payload}")


        # 5. Push message to next queue (Summarize Worker)
        # next_payload = {
        #     "id": task_id,
        #     "transcript": transcript_text,
        #     "message": "Please summarize this"
        # }
        # redis_client.push_task(QUEUE_SUMMARIZE, next_payload)
        # logger.info(f"Pushed to {QUEUE_SUMMARIZE}")

    except Exception as e:
        logger.error(f"Failed to process task {task_id}: {e}", exc_info=True)
        task_record = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if task_record:
            task_record.status = STATUS_FAILED
            db.commit()
    finally:
        # Cleanup file tạm ở local
        if local_file_path:
            engine.cleanup(local_file_path)
        db.close()

def run():
    logger.info("Transcriber Worker Started... Waiting for tasks.")
    try:
        engine = TranscriberEngine()
    except Exception as e:
        logger.critical(f"Failed to load Transcriber Engine: {e}")
        return

    while True:
        try:
            task_payload = redis_client.wait_for_task(QUEUE_TRANSCRIBE, timeout=5)
            if task_payload:
                process_task(engine, task_payload)
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in worker loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()