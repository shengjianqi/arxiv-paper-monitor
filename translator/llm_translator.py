# translator/llm_translator.py

from openai import OpenAI
import time

class AcademicTranslator:
    def __init__(self, api_key, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate(self, text: str) -> str:
        """单条文本翻译"""
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

    def safe_translate(self, text: str, sleep=0.5):
        """带延时的安全翻译，防止触发速率限制"""
        result = self.translate(text)
        time.sleep(sleep)
        return result
