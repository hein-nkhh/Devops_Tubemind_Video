import os
import sys
import time

# Hack import
sys.path.append("/app")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from sqlalchemy.orm import Session
from libs.common.database import SessionLocal
from libs.common.models import VideoTask
from libs.common.logger import get_logger
from libs.common.redis_client import redis_client
from libs.common.constants import QUEUE_SUMMARIZE, STATUS_SUMMARIZING, STATUS_COMPLETED, QUEUE_NOTIFIER

# from core import SummarizeEngine # run local
from src.core import SummarizeEngine # run docker

logger = get_logger("summarize-worker")

def process_task(engine: SummarizeEngine, task_payload: dict):
    db: Session = SessionLocal()
    task_id = task_payload.get("id")
    
    logger.info(f"Processing Summary Task ID: {task_id}")

    try:
        task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if not task or not task.transcript:
            logger.warning("Task invalid or no transcript.")
            return

        # Update status -> summarizing
        task.status = STATUS_SUMMARIZING
        db.commit()

        # Gọi Gemini
        summary_text = engine.generate_summary(task.transcript)

        # Lưu vào DB
        task.summary = summary_text
        task.status = STATUS_COMPLETED
        db.commit()
        logger.info(f"Summary saved for Task {task_id}")

        notifier_payload = {
            "id": task.id,
            "service": "summarizer",
            "status": STATUS_COMPLETED,
            "email": task.email,
            "object_minio_name": task.minio_object_name,
        }

        redis_client.push_task(QUEUE_NOTIFIER, notifier_payload)
        logger.info(f"Pushed notifier message for task {task_id}")

    except Exception as e:
        logger.error(f"Failed task {task_id}: {e}")
    finally:
        db.close()

def run():
    logger.info("Summarize Worker Started...")
    try:
        engine = SummarizeEngine()
    except Exception as e:
        logger.critical(str(e))
        return

    while True:
        try:
            # Lắng nghe Redis
            task_payload = redis_client.wait_for_task(QUEUE_SUMMARIZE, timeout=5)
            if task_payload:
                process_task(engine, task_payload)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()