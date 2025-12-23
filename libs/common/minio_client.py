from minio import Minio
from .config import settings
from minio.error import S3Error
import os

class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET_NAME

    def upload_bytes(self, data, object_name, length):
        # Kiểm tra bucket tồn tại chưa (optional, vì docker-compose đã tạo rồi)
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        self.client.put_object(self.bucket, object_name, data, length)

    def download_file(self, object_name, file_path):
        self.client.fget_object(self.bucket, object_name, file_path)
    
    def upload_file(self, local_path: str, object_name: str):
        size = os.path.getsize(local_path)
        with open(local_path, "rb") as f:
            self.upload_bytes(f, object_name, size)

    def object_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except:
            return False

    def get_models(self, prefix="models/"):
        try:
            objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise RuntimeError(f"MinIO list models failed: {e}")

minio_client = MinioClient()