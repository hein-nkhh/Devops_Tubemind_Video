import os
import sys

import uuid
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.database import get_db, init_db
from libs.common.models import VideoTask
from libs.common.minio_client import minio_client
from libs.common.redis_client import redis_client
from libs.common.constants import QUEUE_TRANSCRIBE, QUEUE_SUMMARIZE, STATUS_PENDING, STATUS_TRANSCRIPTION_DONE, STATUS_COMPLETED, STATUS_SUMMARIZING
from libs.common.logger import get_logger

logger = get_logger("api_gateway")

# from schemas import TaskResponse, LinkInput, SummarizeRequest # run local
from .schemas import TaskResponse, LinkInput, SummarizeRequest # run in docker


router = APIRouter()

@router.post("/upload/video", response_model=TaskResponse)
async def upload_video(
    file: UploadFile = File(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # 1. Tạo tên object cho MinIO (Folder videos)
        file_ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        object_name = f"videos/{unique_name}"

        # 2. Đọc file và upload lên MinIO
        file_content = await file.read()
        file_size = len(file_content)
        minio_client.upload_bytes(file_content, object_name, file_size)

        # 3. Tạo record trong DB PostgreSQL
        new_task = VideoTask(
            filename=file.filename,
            minio_object_name=object_name,
            email=email,
            status=STATUS_PENDING
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # 4. Bắn message vào Redis
        # Format: {"id", "object_minio_name", "message"}
        message_payload = {
            "id": new_task.id,
            "object_minio_name": object_name,
            "message": "Start transcription process"
        }
        redis_client.push_task(QUEUE_TRANSCRIBE, message_payload)

        new_task.message = "Video saved and queued for processing"
        
        return new_task

    except Exception as e:
        logger.error(f"Error processing video upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/link", response_model=TaskResponse)
async def upload_link(
    link_input: LinkInput,
    db: Session = Depends(get_db)
):
    try:
        # 1. Xử lý link như một file text trong MinIO (Folder links)
        unique_name = f"{uuid.uuid4()}.txt"
        object_name = f"links/{unique_name}"
        
        # Chuyển link thành bytes để lưu
        link_content = link_input.url.encode('utf-8')
        minio_client.upload_bytes(link_content, object_name, len(link_content))

        # 2. Tạo record trong DB
        new_task = VideoTask(
            filename=link_input.url, # Với link, filename là URL
            minio_object_name=object_name,
            email=link_input.email,
            status=STATUS_PENDING
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # 3. Bắn message vào Redis
        message_payload = {
            "id": new_task.id,
            "object_minio_name": object_name,
            "message": "Start processing link content"
        }
        redis_client.push_task(QUEUE_TRANSCRIBE, message_payload)

        new_task.message = "Link saved and queued for processing"
        
        # return TaskResponse(
        #     id=new_task.id,
        #     status="queued",
        #     message="Link saved and queued for processing",
        #     minio_object_name=object_name
        # )
        return new_task

    except Exception as e:
        logger.error(f"Error processing link upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/process/summarize/{task_id}", response_model=TaskResponse)
def trigger_summarize(task_id: int, db: Session = Depends(get_db)):
    # 1. Tìm task
    task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    valid_statuses = [STATUS_TRANSCRIPTION_DONE, STATUS_COMPLETED]
    
    # 2. Validate: Phải có transcript rồi mới tóm tắt được
    if task.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Task is in {task.status} state. Cannot summarize yet."
        )

    try:
        # 3. Bắn message vào Redis Queue Summarize
        task.status = STATUS_SUMMARIZING
        db.commit()
        
        payload = {
            "id": task.id,
            "message": "Trigger manual summary"
        }
        redis_client.push_task(QUEUE_SUMMARIZE, payload)
        
        # 4. Trả về thông báo
        return task # Trả về task hiện tại, FE sẽ thấy status cũ nhưng biết là đã gửi lệnh
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/process/summarize-latest", response_model=TaskResponse)
def trigger_summarize_by_user(
    request: SummarizeRequest, 
    db: Session = Depends(get_db)
):
    user_email = request.email

    # 1. Tìm task MỚI NHẤT của Email này
    task = db.query(VideoTask)\
        .filter(VideoTask.email == user_email)\
        .order_by(VideoTask.id.desc())\
        .first()

    if not task:
        raise HTTPException(status_code=404, detail=f"No tasks found for email: {user_email}")

    # 2. Validate trạng thái
    if task.status not in [STATUS_TRANSCRIPTION_DONE, STATUS_COMPLETED]:
        raise HTTPException(
            status_code=400, 
            detail=f"Your latest task (ID: {task.id}) is '{task.status}'. Please wait for transcription to finish."
        )
    
    if task.status == STATUS_SUMMARIZING:
        raise HTTPException(status_code=400, detail="Summarization is already in progress.")

    try:
        # 3. Trigger logic
        task.status = STATUS_SUMMARIZING
        db.commit()

        payload = {
            "id": task.id,
            "message": "Trigger manual summary by user email"
        }
        redis_client.push_task(QUEUE_SUMMARIZE, payload)
        
        # Gán message ảo để trả về cho đẹp
        task.message = f"Triggered summary for latest task ID: {task.id}"
        return task 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))