# translator/llm_translator.py
from openai import OpenAI
import time
import os

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
            print(f"[Translator Error] {e}")
            return "[Translation Failed]"

    def safe_translate(self, text: str, sleep=0.5) -> str:
        """防止速率限制"""
        result = self.translate(text)
        time.sleep(sleep)
        return result
