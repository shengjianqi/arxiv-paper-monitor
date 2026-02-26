# translator/llm_translator.py
from openai import OpenAI
import os
import time
import logging

logger = logging.getLogger(__name__)

class AcademicTranslator:
    def __init__(self, model="gpt-3.5-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate(self, text: str) -> str:
        if not text or not isinstance(text, str) or not text.strip():
            return ""

        prompt = f"""
Translate the following academic text into precise and professional Chinese.

Rules:
- Preserve technical terminology
- Do NOT simplify
- Do NOT paraphrase
- Do NOT summarize
- Keep original structure
- Use formal academic Chinese style

Text:
{text}
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional academic translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"[Translator Error] {e}")
            return "[Translation Failed]"

    def safe_translate(self, text: str, max_retries=5, initial_wait=1):
        """带指数退避的安全翻译"""
        retry = 0
        wait = initial_wait

        while retry < max_retries:
            try:
                return self.translate(text)
            except Exception as e:
                msg = str(e)
                # 检测是否为速率限制（HTTP 429）
                if "429" in msg or "RateLimit" in msg:
                    retry += 1
                    logger.warning(f"⚠️ 遇到速率限制，等待 {wait} 秒重试 ({retry}/{max_retries})")
                    time.sleep(wait)
                    wait *= 2  # 指数退避
                else:
                    logger.error(f"❌ 翻译失败: {e}")
                    return "[Translation Failed]"

        logger.error("❌ 多次重试后翻译仍失败")
        return "[Translation Failed]"
