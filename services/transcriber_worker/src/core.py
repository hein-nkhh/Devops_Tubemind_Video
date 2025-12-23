import os
import whisper
import yt_dlp
import tempfile

from moviepy import AudioFileClip

from libs.common.minio_client import minio_client
from libs.common.config import settings
from libs.common.logger import get_logger
from pathlib import Path

WHISPER_CACHE_DIR = Path.home() / ".cache" / "whisper"
WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

logger = get_logger("transcriber_engine")

TMP_DIR = os.path.join(tempfile.gettempdir(), "tubemind")
os.makedirs(TMP_DIR, exist_ok=True)


class TranscriberEngine:
    def __init__(self):
        self.model = self._load_whisper_model()

    def _load_whisper_model(self):
        model_name = settings.WHISPER_MODEL_SIZE
        model_file = f"{model_name}.pt"

        local_model_path = WHISPER_CACHE_DIR / model_file
        minio_object = f"models/whisper/{model_file}"

        # Case 1: local chưa có -> thử lấy từ MinIO
        if not local_model_path.exists():
            if minio_client.object_exists(minio_object):
                logger.info("Downloading Whisper model from MinIO")
                minio_client.download_file(
                    minio_object,
                    str(local_model_path)
                )
            else:
                logger.info("Loading Whisper model from internet")
                model = whisper.load_model(model_name)

                # Sau khi load xong, file .pt đã nằm trong cache
                if local_model_path.exists():
                    logger.info("Uploading Whisper model to MinIO")
                    minio_client.upload_file(
                        str(local_model_path),
                        minio_object
                    )
                return model

        # Case 2: đã có local -> load từ file
        logger.info("Loading Whisper model from local cache")
        return whisper.load_model(str(local_model_path))
    
    # =========================================================
    # DOWNLOAD AUDIO
    # =========================================================
    def download_from_youtube(self, url: str, video_id: str) -> str:
        """
        Download best audio only (webm/m4a)
        Return local audio path
        """
        output_template = os.path.join(TMP_DIR, f"{video_id}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        logger.info(f"Downloading audio from: {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)

        if not os.path.exists(downloaded_path):
            raise FileNotFoundError(f"Downloaded audio not found: {downloaded_path}")

        return downloaded_path

    # =========================================================
    # CONVERT TO MP3 USING MOVIEPY
    # =========================================================
    def convert_to_mp3(self, input_path: str, video_id: str) -> str:
        """
        Convert audio to mp3 using moviepy
        """
        output_mp3 = os.path.join(TMP_DIR, f"{video_id}.mp3")

        logger.info(f"Converting to mp3: {input_path}")

        audio = AudioFileClip(input_path)
        audio.write_audiofile(output_mp3, codec="mp3", logger=None)
        audio.close()

        if not os.path.exists(output_mp3):
            raise FileNotFoundError(f"MP3 conversion failed: {output_mp3}")

        return output_mp3

    # =========================================================
    # UPLOAD TO MINIO
    # =========================================================
    def upload_audio_to_minio(self, local_path: str) -> str:
        object_name = f"videos/{os.path.basename(local_path)}"
        size = os.path.getsize(local_path)

        with open(local_path, "rb") as f:
            minio_client.upload_bytes(f, object_name, size)

        logger.info(f"Uploaded to MinIO: {object_name}")
        return object_name

    # =========================================================
    # TRANSCRIBE
    # =========================================================
    def transcribe_file(self, local_path: str) -> str:
        logger.info(f"Transcribing: {local_path}")
        result = self.model.transcribe(local_path)
        return result["text"]
