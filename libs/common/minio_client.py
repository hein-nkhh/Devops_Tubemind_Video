from minio import Minio
from .config import settings
from io import BytesIO
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
        
        if isinstance(data, (bytes, bytearray)):
            data_stream = BytesIO(data)
            size = length if length is not None else len(data)
        
        else:
            data_stream = data
            if length is None:
                data_stream.seek(0, os.SEEK_END)
                size = data_stream.tell()
                data_stream.seek(0)
            else:
                size = length
                    
        self.client.put_object(self.bucket, object_name, data_stream, size)

    def download_file(self, object_name, file_path):
        self.client.fget_object(self.bucket, object_name, file_path)

minio_client = MinioClient()