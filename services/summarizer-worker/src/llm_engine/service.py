
from pathlib import Path
from .model import client
from src.config import Config

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "promts" / "summary_promt.txt"

# Hàm tóm tắt văn bản sử dụng mô hình LLM
def summarize_text(text):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    final_prompt = prompt_template.replace("{{TEXT}}", text)
    # Gửi yêu cầu tới mô hình
    response = client.generate_content(final_prompt)
    return response.text