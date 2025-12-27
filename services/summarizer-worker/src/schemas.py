from pydantic import BaseModel

class SummaryRequest(BaseModel):
    transcript: str

class SummaryResponse(BaseModel):
    summary: str

class TestPushMessage(BaseModel):
    filename: str
    minio_object_name: str
    email: str
    transcript: str
    
