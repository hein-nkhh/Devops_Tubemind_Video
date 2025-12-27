import os
from google import genai
from dotenv import load_dotenv

# Load .env nếu không phải production
if os.getenv("ENV") != "production":
    load_dotenv()

# Lấy key AI từ env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUMARIZER_MODEL = os.getenv("SUMARIZER_MODEL")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")
if not SUMARIZER_MODEL:
    raise RuntimeError("SUMARIZER_MODEL is not set")

client = genai.Client()

PROMPT_TEMPLATE = """Bạn là một hệ thống tóm tắt văn bản.

Nhiệm vụ:
- Tóm tắt đoạn văn bản dưới đây thành một bản tóm tắt ngắn gọn, súc tích.
- Giữ lại các ý chính, thông tin quan trọng.
- Không thêm thông tin mới, không suy đoán.
- Viết bằng ngôn ngữ giống với ngôn ngữ của văn bản gốc.

Yêu cầu:
- Độ dài: 4-6 câu.
- Văn phong trung lập, khách quan.
- Không dùng gạch đầu dòng, viết thành đoạn văn liền mạch.

Văn bản cần tóm tắt:
{text}
"""

def summarize_text(text: str) -> str:
    if not text or not text.strip():
        return ""

    prompt = PROMPT_TEMPLATE.format(text=text.strip())
    response = client.models.generate_content(
        model=SUMARIZER_MODEL,
        contents=prompt,
    )

    return response.text.strip()
