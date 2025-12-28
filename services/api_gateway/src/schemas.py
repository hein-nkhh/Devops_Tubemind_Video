from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema cho input là Link
class LinkInput(BaseModel):
    url: str
    email: str

# Schema cho response trả về client ngay lập tức
class TaskResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str
    minio_object_name: str
    
    message: Optional[str] = None
    
    # Field cho detailed info (khi cần)
    transcript: Optional[str] = None
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
class SummarizeRequest(BaseModel):
    email: str