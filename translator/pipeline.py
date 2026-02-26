# translator/pipeline.py

from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder

import time
import openai

def safe_translate(messages, max_retries=5):
    """
    使用指数退避策略安全调用 OpenAI ChatCompletion
    messages: [{"role": "user", "content": "..."}]
    """
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 可根据需要换 gpt-4
                messages=messages
            )
            return response
        except openai.error.RateLimitError:
            wait = 2 ** retries
            print(f"Rate limit exceeded, retrying in {wait}s...")
            time.sleep(wait)
            retries += 1
    raise Exception("Exceeded retry limit")

class TranslationPipeline:

    def __init__(self, api_key, batch_size=5, delay_between_batches=0.5):
        self.translator = AcademicTranslator(api_key)
        self.builder = TranslationEmailBuilder()
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches

    def process(self, papers_raw):
        """
        papers_raw: [
            {"title": "...", "abstract": "...", "link": "..."}
        ]
        返回 email_body
        """
        results = []

        # 将标题和摘要分批处理
        for i in range(0, len(papers_raw), self.batch_size):
            batch = papers_raw[i:i+self.batch_size]

            # 构建批量翻译内容
            messages = [{"role": "user",
                         "content": "Translate the following titles and abstracts to Chinese, "
                                    "return as JSON list with 'title_zh' and 'abstract_zh':\n" +
                                    "\n".join(
                                        f"{idx} Title: {p['title']}\nAbstract: {p.get('abstract','')}"
                                        for idx, p in enumerate(batch, start=1)
                                    )}]
            # 调用 safe_translate
            response = safe_translate(messages)
            translation_text = response['choices'][0]['message']['content']

            # 尝试解析为 JSON（假设返回格式可解析）
            import json
            try:
                translations = json.loads(translation_text)
            except json.JSONDecodeError:
                # 返回非标准 JSON，则按换行拆分（最保底）
                lines = [line.strip() for line in translation_text.split("\n") if line.strip()]
                translations = []
                for idx, p in enumerate(batch):
                    t = lines[idx*2] if idx*2 < len(lines) else ""
                    a = lines[idx*2+1] if idx*2+1 < len(lines) else ""
                    translations.append({"title_zh": t, "abstract_zh": a})

            # 添加到结果
            for p, trans in zip(batch, translations):
                results.append({
                    "title_en": p["title"],
                    "title_zh": trans.get("title_zh", ""),
                    "abstract_en": p.get("abstract",""),
                    "abstract_zh": trans.get("abstract_zh", ""),
                    "url": p.get("link", "")
                })

            # 批之间延迟，降低 429 概率
            time.sleep(self.delay_between_batches)

        email_body = self.builder.build(results)
        return email_body
