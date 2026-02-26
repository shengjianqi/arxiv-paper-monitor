# translator/llm_translator.py
from openai import OpenAI
import os
import time
import random

class AcademicTranslator:
    def __init__(self, model="gpt-3.5-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate(self, text: str) -> str:
        """直接调用OpenAI接口进行翻译"""
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

    def safe_translate(self, text: str, max_retries=5, max_wait=10, base_wait=1):
        """带指数退避和随机抖动的安全翻译"""
        retry = 0
        wait = base_wait

        while retry < max_retries:
            try:
                result = self.translate(text)
                # 每次成功请求后等待一定时间，避免过快
                time.sleep(wait + random.uniform(0, 0.5))
                return result
            except Exception as e:
                retry += 1
                print(f"[Translator] 错误或速率限制，等待 {wait:.1f} 秒后重试（{retry}/{max_retries}）")
                time.sleep(wait + random.uniform(0, 0.5))
                wait = min(wait * 2, max_wait)  # 指数退避，限制最大等待时间
        return "[Translation Failed]"
