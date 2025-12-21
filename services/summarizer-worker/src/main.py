from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.llm_engine.service import summarize_text

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}


class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = 100

@app.post("/summarize")
def summarize(req: SummarizeRequest) -> dict:
    try:
        summary = summarize_text(req.text)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/{id}")
def get_summary(id: str) -> dict:
    try:
        # Placeholder for fetching summary by ID
        summary = "This is a placeholder summary for ID: " + id
        
        return {"id": id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def proccess_message(message):
    print("Received message:", message)
    # Add your message processing logic here