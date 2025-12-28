import os
import sys

import google.generativeai as genai

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT_DIR)

from libs.common.config import settings
from libs.common.logger import get_logger

logger = get_logger("summarize_engine")

class SummarizeEngine:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is missing!")
            raise ValueError("GEMINI_API_KEY is required")
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Dùng bản flash cho nhanh và rẻ
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_summary(self, transcript_text: str) -> str:
        if not transcript_text:
            return ""

        logger.info("Sending request to Gemini API...")
        prompt = f"""
        Bạn là một trợ lý AI chuyên tóm tắt nội dung video.

        NGỮ CẢNH:
        - Văn bản bên dưới là transcript được tạo tự động từ một video BẰNG TIẾNG ANH.
        - Transcript có thể có lỗi nhận dạng, thiếu dấu câu hoặc câu không hoàn chỉnh.
        - Người dùng KHÔNG muốn đọc transcript gốc mà chỉ muốn hiểu nhanh nội dung video.

        NHIỆM VỤ:
        - Hiểu nội dung transcript tiếng Anh.
        - Tóm tắt lại nội dung video bằng TIẾNG VIỆT, rõ ràng và dễ hiểu.

        YÊU CẦU:
        1. Chỉ sử dụng thông tin có trong transcript, không thêm kiến thức bên ngoài.
        2. Giữ đúng ý của người nói, không xuyên tạc.
        3. Loại bỏ các phần nói lan man, lặp ý, filler words.
        4. Nếu có ví dụ, hãy diễn đạt lại ngắn gọn bằng tiếng Việt.
        5. Nếu transcript không rõ ràng, hãy suy luận hợp lý dựa trên ngữ cảnh nói chuyện (nhưng không bịa).

        ĐỊNH DẠNG OUTPUT:
        - Tiêu đề (tiếng Việt)
        - Tóm tắt ngắn (3–5 câu)
        - Các ý chính (bullet points)

        TRANSCRIPT (EN):
        
        "{transcript_text}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text
            return "Không thể tạo tóm tắt."
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            raise e