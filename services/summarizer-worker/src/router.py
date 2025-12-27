import os
import sys

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.database import get_db
from libs.common.models import VideoTask
from libs.common.redis_client import redis_client
from libs.common.constants import QUEUE_SUMMARIZE, STATUS_PENDING, QUEUE_NOTIFY

from schemas import SummaryRequest, SummaryResponse, TestPushMessage # run local
# from .schemas import SummaryRequest, SummaryRequest # run in docker

from llm_engine import summarize_text # run local
# from .llm_engine import summarize_text # run in docker

router = APIRouter()

# Api endpoint để tóm tắt văn bản trực tiếp
@router.post("/")
def summarize(request: SummaryRequest) -> SummaryResponse:
    try:
        summarized_text = summarize_text(request.transcript)
        return SummaryResponse(summary=summarized_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint push message into queue summarize for testing
@router.post("/push-summarize-queue")
def test_push_summarize_queue(request: TestPushMessage, db: Session = Depends(get_db)) -> dict:
    # Tạo task giả để kiểm tra queue
    try:
        # Tạo task giả trong DB
        new_task = VideoTask(
            filename=request.filename,
            minio_object_name=request.minio_object_name,
            email=request.email,
            transcript=request.transcript,
            status=STATUS_PENDING
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        # Đẩy task vào Redis queue transcribe
        redis_client.push_task(QUEUE_SUMMARIZE, {
            "id": new_task.id,
            "object_minio_name": new_task.minio_object_name,
            "transcript": new_task.transcript
        })
        
        return {"message": "Test task created and pushed to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint pop message into queue notify for testing
@router.get("/pop-notify-queue")
def test_pop_notify_queue() -> dict:
    # Tạo task giả để kiểm tra queue
    try:
        notify_summary = redis_client.wait_for_task(QUEUE_NOTIFY)
        if not notify_summary:
            raise HTTPException(status_code=404, detail="No notification message in queue")
        
        return {"data": notify_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


