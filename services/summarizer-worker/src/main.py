from fastapi import FastAPI, HTTPException, UploadFile, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from src.llm_engine.service import summarize_text
from src.database.database import SessionLocal
from src.database.database_models import SummaryJob, Summary, Base
from src.logger import logger
from sqlalchemy import text
from sqlalchemy import create_engine
import os
import uuid
from datetime import datetime

Base.metadata.create_all(bind=SessionLocal.kw['bind'])


# Khởi tạo ứng dụng FastAPI
app = FastAPI()

@app.get("/health")

# API kiểm tra tình trạng server
def health_check():
    return {"status": "healthy"}


# Model dữ liệu cho yêu cầu tóm tắt
class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = 100

# API nhận URL, kiểm tra transcript, trả về trạng thái hoặc summary
@app.get("/summary/by-url")
def get_summary_by_url(youtube_url: str):
    """
    Nhận vào youtube_url, kiểm tra ở DB transcriber-worker:
    - Nếu chưa có transcript: trả về thông báo chưa transcribe
    - Nếu có transcript: trả về summary nếu đã tóm tắt, hoặc thông báo chưa tóm tắt
    """
    # Kết nối DB transcriber-worker (giả sử cùng DB, hoặc dùng SQLAlchemy engine khác nếu cần)
    from services.transcriber_worker.src.database.database import SessionLocal as TranscriberSession
    from services.transcriber_worker.src.database.database_models import VideoSource, TranscriptJob, Transcript
    db_tr = TranscriberSession()
    db = SessionLocal()
    # Tìm video_id từ youtube_url
    video_source = db_tr.query(VideoSource).filter_by(youtube_url=youtube_url).first()
    if not video_source:
        db_tr.close()
        return {"status": "not_found", "message": "Video chưa được upload/transcribe"}
    video_id = video_source.video_id
    # Tìm transcript job
    transcript_job = db_tr.query(TranscriptJob).filter_by(video_id=video_id).order_by(TranscriptJob.started_at.desc()).first()
    if not transcript_job or transcript_job.status != "done":
        db_tr.close()
        return {"status": "not_transcribed", "message": "Video chưa được transcribe"}
    # Lấy transcript
    transcript = db_tr.query(Transcript).filter_by(job_id=transcript_job.id).first()
    if not transcript:
        db_tr.close()
        return {"status": "not_transcribed", "message": "Transcript chưa sẵn sàng"}
    # Kiểm tra đã có summary chưa
    summary_job = db.query(SummaryJob).filter_by(id=str(transcript_job.id)).first()
    if not summary_job or summary_job.status != "done":
        db_tr.close()
        db.close()
        return {"status": "not_summarized", "message": "Transcript đã sẵn sàng, nhưng chưa được tóm tắt"}
    summary = db.query(Summary).filter_by(job_id=summary_job.id).first()
    db_tr.close()
    db.close()
    if not summary:
        return {"status": "not_summarized", "message": "Chưa có summary"}
    return {"status": "summarized", "summary": summary.content}

# API CRUD cho summary
from fastapi import Query

# Tạo summary thủ công
@app.post("/summary/")
def create_summary_manual(job_id: str = Query(...), content: str = Query(...)):
    db = SessionLocal()
    summary = Summary(job_id=job_id, content=content, created_at=datetime.now())
    db.add(summary)
    db.commit()
    db.refresh(summary)
    db.close()
    return {"id": summary.id, "job_id": summary.job_id, "content": summary.content}

# Đọc summary theo id
@app.get("/summary/{summary_id}")
def read_summary(summary_id: str):
    db = SessionLocal()
    summary = db.query(Summary).filter_by(id=summary_id).first()
    db.close()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"id": summary.id, "job_id": summary.job_id, "content": summary.content}

# Sửa summary
@app.put("/summary/{summary_id}")
def update_summary(summary_id: str, content: str = Query(...)):
    db = SessionLocal()
    summary = db.query(Summary).filter_by(id=summary_id).first()
    if not summary:
        db.close()
        raise HTTPException(status_code=404, detail="Summary not found")
    summary.content = content
    db.commit()
    db.refresh(summary)
    db.close()
    return {"id": summary.id, "job_id": summary.job_id, "content": summary.content}

# Xóa summary
@app.delete("/summary/{summary_id}")
def delete_summary(summary_id: str):
    db = SessionLocal()
    summary = db.query(Summary).filter_by(id=summary_id).first()
    if not summary:
        db.close()
        raise HTTPException(status_code=404, detail="Summary not found")
    db.delete(summary)
    db.commit()
    db.close()
    return {"message": "Summary deleted"}


