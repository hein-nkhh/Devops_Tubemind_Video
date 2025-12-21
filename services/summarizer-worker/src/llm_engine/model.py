from src.config import api_key, model_name
import google.generativeai as genai

genai.configure(api_key=api_key)
client = genai.GenerativeModel(model_name=model_name)