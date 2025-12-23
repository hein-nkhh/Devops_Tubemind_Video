import os
import sys
import time

sys.path.append(os.getcwd())

from libs.common.config import settings
from libs.common.database import init_db, SessionLocal
from libs.common.models import VideoTask
from libs.common.redis_client import redis_client
from libs.common.minio_client import minio_client
from libs.common.email_client import send_email
from sqlalchemy import text

def print_pass(msg):
    print(f"[PASS]{msg}")
    
def print_fail(msg, error):
    print(f"[FAIL] {msg}")
    print(f"Error: {error}")
    
def test_config():
    print("\n--- 1. Testing Config ---")
    try:
        if settings.POSTGRES_HOST == "localhost":
            print_pass(f"Loaded config from .env.local (DB Host: {settings.POSTGRES_HOST})")
        else:
            print(f"Warning: Config loaded: {settings.POSTGRES_HOST}. Create .env.local?")
    except Exception as e:
        print_fail("Config load failed", e)
       
def test_database():
    print("\n--- 2. Testing Database (Postgres) ---")
    try:
        # 1. Test kết nối & Tạo bảng
        init_db()
        print_pass("Database connected & Tables created")

        # 2. Test Insert
        db = SessionLocal()
        # Xóa dữ liệu cũ của test trước (nếu có)
        db.query(VideoTask).filter(VideoTask.email == "test@local").delete()
        
        new_task = VideoTask(
            filename="test.mp4", 
            minio_object_name="test-obj", 
            email="test@local", 
            status="testing"
        )
        db.add(new_task)
        db.commit()
        print_pass("Insert dummy record success")

        # 3. Test Query
        task = db.query(VideoTask).filter(VideoTask.email == "test@local").first()
        if task:
            print_pass(f"Query record success: ID={task.id}, Status={task.status}")
        else:
            raise Exception("Record not found after insert")
        
        db.close()
    except Exception as e:
        print_fail("Database test failed", e)
        
        
def test_redis():
    print("\n--- 3. Testing Redis ---")
    test_queue = "queue:test_libs"
    try:
        # 1. Push
        payload = {"msg": "Hello Redis"}
        redis_client.push_task(test_queue, payload)
        print_pass("Push task success")

        # 2. Pop
        result = redis_client.wait_for_task(test_queue, timeout=2)
        if result and result['msg'] == "Hello Redis":
            print_pass(f"Pop task success: {result}")
        else:
            raise Exception("Failed to pop task or wrong data")
    except Exception as e:
        print_fail("Redis test failed", e)
         
def test_redis_visible():
    print("\n--- Testing Redis Visible ---")
    test_queue = "queue:test_libs"
    payload = {"msg": "Hello Redis"}

    redis_client.push_task(test_queue, payload)
    print_pass("Push task success")

    print("Now open Redis Insight and check key:", test_queue)
    input("Press Enter to pop...")

    result = redis_client.wait_for_task(test_queue, timeout=5)
    print_pass(f"Popped: {result}")
    
def test_minio():
    print("\n--- 4. Testing MinIO ---")
    try:
        # Tạo file giả
        file_name = "test_minio.txt"
        with open(file_name, "w") as f:
            f.write("This is a test file for MinIO")

        # 1. Upload
        object_name = "test_upload.txt"
        file_size = os.path.getsize(file_name)
        with open(file_name, "rb") as f:
            minio_client.upload_bytes(f, object_name, file_size)
        print_pass("Upload file success")

        # 2. Download
        download_path = "test_downloaded.txt"
        minio_client.download_file(object_name, download_path)
        
        if os.path.exists(download_path):
            print_pass("Download file success")
            os.remove(download_path)
        else:
            raise Exception("Downloaded file not found")

        # Dọn dẹp
        os.remove(file_name)

    except Exception as e:
        print_fail("MinIO test failed", e)

def test_email():
    print("\n--- 5. Testing Email (MailHog) ---")
    try:
        success = send_email("test@user.com", "Test Subject", "This is a test body")
        if success:
            print_pass("Email sent to MailHog successfully")
        else:
            raise Exception("Send email function returned False")
    except Exception as e:
        print_fail("Email test failed", e)
        
         
if __name__ == "__main__":
    # test_config()
    # test_database()
    # test_redis()
    # test_redis_visible()
    # test_minio()
    test_email()