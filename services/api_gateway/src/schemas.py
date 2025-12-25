from pydantic import BaseModel
from typing import Optional

# Schema cho input là Link
class LinkInput(BaseModel):
    url: str
    email: str

# Schema cho response trả về client ngay lập tức
class TaskResponse(BaseModel):
    id: int
    status: str
    message: str
    minio_object_name: str