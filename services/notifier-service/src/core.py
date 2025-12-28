from libs.common.email_client import send_email
from libs.common.database import SessionLocal
from libs.common.models import VideoTask
from libs.common.constants import (
    STATUS_TRANSCRIPTION_DONE,
    STATUS_COMPLETED,
)

def process_message(message: dict):

    print("\n========== NOTIFIER RAW MESSAGE ==========")
    print(message)

    task_id = message.get("id") or message.get("task_id")
    service = message.get("service")

    raw_status = message.get("status")
    status = raw_status.lower() if isinstance(raw_status, str) else raw_status

    email = message.get("email")
    object_minio_name = message.get("object_minio_name")

    print("---- Normalized fields ----")
    print("task_id =", task_id)
    print("service =", service)
    print("raw_status =", raw_status)
    print("normalized status =", status)
    print("STATUS_COMPLETED =", STATUS_COMPLETED)
    print("STATUS_TRANSCRIPTION_DONE =", STATUS_TRANSCRIPTION_DONE)
    print("-----------------------------------------")

    if not task_id or not service or not status:
        print("[Notifier] Invalid message:", message)
        return

    db = SessionLocal()

    try:
        task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if not task:
            print(f"[Notifier] Task {task_id} not found")
            return

        # ===============================
        # TRANSCRIBER DONE
        # ===============================
        if service == "transcriber" and status == STATUS_TRANSCRIPTION_DONE:
            print(">>> MATCH: TRANSCRIBER DONE")

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
            print(">>> MATCH: SUMMARIZER DONE")

            task.status = STATUS_COMPLETED
            task.message = "Summary completed"

            if email:
                send_email(
                    email,
                    "Your summary is ready",
                    f"Task {task_id} summary completed."
                )

        else:
            print("❌ NOT MATCHED ANY CASE")

        db.commit()

    except Exception as e:
        db.rollback()
        print("[Notifier] ERROR:", e)

    finally:
        db.close()
