import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.database import init_db
# from router import router # run local
from .router import router # run in docker


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TubeMind API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.on_event("startup")
def on_startup():
    init_db()
    
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",      
        host="0.0.0.0",
        port=8000,
        reload=True     
    )