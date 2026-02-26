# translator/llm_translator.py
from openai import OpenAI
import os
import time

class AcademicTranslator:
    def __init__(self, model="gpt-3.5-turbo"):
        """
        自动从环境变量读取 OPENAI_API_KEY
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请在环境变量中设置 OPENAI_API_KEY")
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
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional academic translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        return resp.choices[0].message.content.strip()

    def safe_translate(self, text: str, max_retries=5):
        """
        带指数退避的安全翻译，处理 429 Too Many Requests
        """
        wait = 1
        for attempt in range(max_retries):
            try:
                return self.translate(text)
            except Exception as e:
                msg = str(e).lower()
                if "rate limit" in msg or "429" in msg:
                    print(f"[Translator] 速率限制，等待 {wait} 秒后重试 ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    wait *= 2
                    continue
                print(f"[Translator Error] {e}")
                return "[Translation Failed]"
        return "[Translation Failed]"
