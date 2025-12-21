from dotenv import load_dotenv
import os

load_dotenv() 

api_key = os.getenv("API_KEY")
model_name = os.getenv("AI_MODEL_NAME", "models/gemini-1.5-flash")
