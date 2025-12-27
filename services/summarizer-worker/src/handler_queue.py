import os
import sys

from fastapi import Depends
from sqlalchemy.orm import Session

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.database import get_db
from libs.common.models import VideoTask
from libs.common.redis_client import redis_client
from libs.common.constants import NOTIF_SUMMARY_DONE, QUEUE_NOTIFY, QUEUE_SUMMARIZE

from llm_engine import summarize_text # run local
# from .llm_engine import summarize_text # run in docker

# Xử lý task tóm tắt từ Redis queue
def process_summary_task(db: Session = Depends(get_db)):
    try:
        # Lấy task từ Redis queue summarize
        # message format: {"id", "object_minio_name", "transcript"}
        task = redis_client.wait_for_task(QUEUE_SUMMARIZE)
        if not task:
            return None
                
        task_id = task.get("id")
        object_minio_name = task.get("object_minio_name")
        transcript_text = task.get("transcript")
        
        if not task_id or not object_minio_name or not transcript_text:
            print("Invalid task format")
            return None

        # Tóm tắt nội dung
        summary = summarize_text(transcript_text)
        
        # Lưu summary vào DB
        task_record = db.query(VideoTask).filter(VideoTask.id == task_id).first()
        if not task_record:
            print(f"Task {task_id} not found in DB")
            return None
        
        task_record.summary = summary
        task_record.status = "completed" 
        db.commit()
        db.refresh(task_record)
        
        # Push message thông báo hoàn thành tóm tắt vào Redis
        # Message format: {"task_id", "summary", "object_minio_name", "message_type"}
        notification_payload = {
            "task_id": task_id,
            "summary": summary,
            "object_minio_name": object_minio_name,
            "message_type": NOTIF_SUMMARY_DONE,
        }
        
        redis_client.push_task(QUEUE_NOTIFY, notification_payload)  
              
    except Exception as e:
        print(f"Error summarizing task {task_id}: {e}")
        return None