import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

import whisper
import yt_dlp
import tempfile
from pathlib import Path
from moviepy import AudioFileClip

from libs.common.minio_client import minio_client
from libs.common.config import settings
from libs.common.logger import get_logger

logger = get_logger("transcriber_engine")

WHISPER_CACHE_DIR = Path("/root/.cache/whisper")
WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

TMP_DIR = os.path.join(tempfile.gettempdir(), "tubemind")
os.makedirs(TMP_DIR, exist_ok=True)

class TranscriberEngine:
    def __init__(self):
        self.model = self._load_whisper_model()

    def _load_whisper_model(self):
        model_name = settings.WHISPER_MODEL_SIZE
        logger.info(f"Loading Whisper model: {model_name}... (CPU)")
        return whisper.load_model(model_name, device="cpu", download_root=str(WHISPER_CACHE_DIR))

    def download_file_from_minio(self, object_name: str) -> str:
        local_filename = os.path.basename(object_name)
        local_path = os.path.join(TMP_DIR, local_filename)
        logger.info(f"Downloading from MinIO: {object_name} -> {local_path}")
        minio_client.download_file(object_name, local_path)
        return local_path

    def read_url_from_minio_text(self, object_name: str) -> str:
        local_path = self.download_file_from_minio(object_name)
        with open(local_path, 'r') as f:
            url = f.read().strip()
        os.remove(local_path) 
        return url

    def download_from_youtube(self, url: str) -> str:
        import uuid
        file_id = str(uuid.uuid4())
        # Lưu ý: output template để extension tự động, nhưng yt-dlp sẽ trả về file cụ thể
        output_template = os.path.join(TMP_DIR, f"{file_id}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best", # Lấy audio tốt nhất cho nhẹ
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            logger.info(f"Downloading audio from Youtube: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_path = ydl.prepare_filename(info)
            return downloaded_path
        except Exception as e:
            logger.error(f"Error downloading from Youtube: {e}")
            raise e

    # --- NEW FUNCTION ---
    def upload_file_to_minio(self, local_path: str, folder_name: str) -> str:
        """Upload file từ local lên MinIO vào folder chỉ định"""
        filename = os.path.basename(local_path)
        object_name = f"{folder_name}/{filename}"
        file_size = os.path.getsize(local_path)

        logger.info(f"Uploading to MinIO: {local_path} -> {object_name}")
        
        with open(local_path, "rb") as f:
            minio_client.upload_bytes(f, object_name, file_size)
            
        return object_name
    # --------------------

    def transcribe_file(self, local_path: str) -> str:
        logger.info(f"Transcribing file: {local_path}")
        result = self.model.transcribe(local_path, fp16=False) 
        return result["text"]

    def cleanup(self, file_path: str):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up: {file_path}")