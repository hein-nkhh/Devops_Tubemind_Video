from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chuỗi kết nối: postgresql://user:password@localhost/db_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password123@localhost/fastapi_db"

# Tạo engine kết nối
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo Session để thao tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Class cha cho các model
Base = declarative_base()


def get_transcriber_data():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_summarizer_data_by_url(url: str):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_summarizer_data(id: str):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_summary(db_session, summary_data):
    pass