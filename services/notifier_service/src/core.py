from libs.common.email_client import send_email
from libs.common.database import SessionLocal
from libs.common.models import VideoTask
from libs.common.constants import (
    STATUS_TRANSCRIPTION_DONE,
    STATUS_COMPLETED,
)
from libs.common.logger import get_logger

logger = get_logger("notifier-core")

def process_message(message: dict):

    logger.info("\n========== NOTIFIER RAW MESSAGE ==========")
    logger.info(message)

    task_id = message.get("id") or message.get("task_id")
    service = message.get("service")

    raw_status = message.get("status")
    status = raw_status.lower() if isinstance(raw_status, str) else raw_status

    email = message.get("email")
    object_minio_name = message.get("object_minio_name")

    logger.info("---- Normalized fields ----")
    logger.info("task_id = %s", task_id)
    logger.info("service = %s", service)
    logger.info("raw_status = %s", raw_status)
    logger.info("normalized status = %s", status)
    logger.info("STATUS_COMPLETED = %s", STATUS_COMPLETED)
    logger.info("STATUS_TRANSCRIPTION_DONE = %s", STATUS_TRANSCRIPTION_DONE)
    logger.info("-----------------------------------------")

    if not task_id or not service or not status:
        logger.error("[Notifier] Invalid message: %s", message)
        return

    db = SessionLocal()

    try:
        task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if not task:
            logger.error("[Notifier] Task %s not found", task_id)
            return

        # ===============================
        # TRANSCRIBER DONE
        # ===============================
        if service == "transcriber" and status == STATUS_TRANSCRIPTION_DONE:
            logger.info(">>> MATCH: TRANSCRIBER DONE")

            task.status = STATUS_TRANSCRIPTION_DONE
            task.message = "Transcription completed"

            if email:
                send_email(
                    email,
                    "Your transcription is ready",
                    f"Task {task_id} transcription completed."
                )

        # ===============================
        # SUMMARIZER DONE
        # ===============================
        elif service == "summarizer" and status == STATUS_COMPLETED:
            logger.info(">>> MATCH: SUMMARIZER DONE")

            task.status = STATUS_COMPLETED
            task.message = "Summary completed"

            if email:
                send_email(
                    email,
                    "Your summary is ready",
                    f"Task {task_id} summary completed."
                )

        else:
            logger.info("NOT MATCHED ANY CASE")

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error("[Notifier] ERROR: %s", e)

    finally:
        db.close()
