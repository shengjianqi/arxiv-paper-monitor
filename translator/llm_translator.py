# translator/llm_translator.py
import os
import time
from openai import OpenAI

class AcademicTranslator:
    def __init__(self, model="gpt-3.5-turbo", max_wait=2.0):
        """
        max_wait: 每次请求之间最大等待时间（秒）
        """
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_wait = max_wait

    def translate(self, text: str) -> str:
        """单次翻译"""
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
            print(f"[Translator Error] {e}")
            return "[Translation Failed]"

    def safe_translate(self, text: str, max_retries=5):
        """带指数退避的安全翻译"""
        retry = 0
        wait = 1  # 初始等待1秒
        while retry < max_retries:
            try:
                result = self.translate(text)
                time.sleep(self.max_wait)  # 请求间隔
                return result
            except Exception as e:
                retry += 1
                print(f"[Translator] 出现异常，等待 {wait} 秒后重试（{retry}/{max_retries}）: {e}")
                time.sleep(wait)
                wait = min(wait * 2, self.max_wait)  # 指数退避，但不超过最大等待时间
        return "[Translation Failed]"
