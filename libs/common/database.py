from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base, VideoTask
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
def delete_db():
    db = SessionLocal()
    try:
        db.query(VideoTask).delete()
        db.commit()
    finally:
        db.close()
        
if __name__ == "__main__":
    delete_db()