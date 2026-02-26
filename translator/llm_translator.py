# translator/llm_translator.py
from openai import OpenAI
import os
import time

class AcademicTranslator:
    def __init__(self, model="gpt-3.5-turbo"):
        """
        初始化翻译器，从环境变量读取 OPENAI_API_KEY
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("环境变量 OPENAI_API_KEY 未设置")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate(self, text: str) -> str:
        """
        单条文本翻译
        """
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

    def safe_translate(self, text: str, max_retries=5, batch_size=500):
        """
        安全翻译，带指数退避
        对文本过长时分批处理
        """
        if not text or not isinstance(text, str):
            return ""

        # 分批处理（按字符数）
        chunks = [text[i:i+batch_size] for i in range(0, len(text), batch_size)]
        translated_chunks = []

        for chunk in chunks:
            retry = 0
            wait = 1  # 初始等待 1 秒
            while retry < max_retries:
                try:
                    translated = self.translate(chunk)
                    translated_chunks.append(translated)
                    break
                except Exception as e:
                    retry += 1
                    print(f"[Translator] 出现错误或速率限制，等待 {wait}s 后重试 ({retry}/{max_retries})")
                    time.sleep(wait)
                    wait *= 2  # 指数退避
                    if retry >= max_retries:
                        translated_chunks.append("[Translation Failed]")
        return "".join(translated_chunks)
