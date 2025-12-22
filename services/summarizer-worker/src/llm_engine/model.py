from src.config import Config
import google.generativeai as genai

genai.configure(api_key=Config.API_KEY)
client = genai.GenerativeModel(model_name=Config.MODEL_NAME)