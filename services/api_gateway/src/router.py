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
from libs.common.constants import QUEUE_TRANSCRIBE, STATUS_PENDING

# from schemas import TaskResponse, LinkInput # run local
from .schemas import TaskResponse, LinkInput # run in docker


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

        return TaskResponse(
            id=new_task.id,
            status="queued",
            message="Video uploaded and queued for processing",
            minio_object_name=object_name
        )

    except Exception as e:
        print(f"Error processing video: {e}")
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

        return TaskResponse(
            id=new_task.id,
            status="queued",
            message="Link saved and queued for processing",
            minio_object_name=object_name
        )

    except Exception as e:
        print(f"Error processing link: {e}")
        raise HTTPException(status_code=500, detail=str(e))