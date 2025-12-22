
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
	API_KEY = os.getenv("API_KEY")
	MODEL_NAME = os.getenv("AI_MODEL_NAME", "models/gemini-1.5-flash")
	# Thêm các biến cấu hình khác nếu cần
	DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///summarizer.db")
