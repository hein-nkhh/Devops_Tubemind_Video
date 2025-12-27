import uvicorn
import sys
import os
import threading
from contextlib import asynccontextmanager

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.database import init_db, SessionLocal
from router import router # run local
# from .router import router # run in docker

from handler_queue import process_summary_task # run local
# from .handler_queue import process_summary_task # run in docker

def run_worker():
    """Background worker - chạy trong thread riêng"""
    print("🚀 Worker thread started, listening to Redis queue...")
    
    while True:
        db = SessionLocal()
        try:
            print("⏳ Waiting for task from queue...")
            process_summary_task(db)
        except Exception as e:
            print(f"❌ Worker error: {e}")
        finally:
            db.close()
            
from fastapi import FastAPI
app = FastAPI(title="Summarizer Worker")

@asynccontextmanager
async def lifespan(app: FastAPI):    
    # Startup
    init_db()  # tạo tables nếu chưa có
    
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    print("✅ Background worker started!")
    
    yield  
    
    # Shutdown
    print("🛑 App shutting down...")

app.router.lifespan_context = lifespan
    
app.include_router(router, prefix="/api/v1/summarizer")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "summarizer-worker"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",      
        host="0.0.0.0",
        port=8001,
        reload=True     
    )