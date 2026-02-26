# translator/pipeline.py

from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder

import time
import openai

def safe_translate(messages):
    retries = 0
    while retries < 5:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
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

    def __init__(self, api_key):
        self.translator = AcademicTranslator(api_key)
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        papers_raw: 来自 arxiv 抓取模块的数据
        结构示例:
        [
            {
                "title": "...",
                "summary": "...",
                "link": "https://arxiv.org/abs/xxxx"
            }
        ]
        """

        results = []

        for p in papers_raw:
            title_en = p["title"]
            abstract_en = p.get("abstract", "")

            title_zh = self.translator.safe_translate(title_en)
            abstract_zh = self.translator.safe_translate(abstract_en)

            results.append({
                "title_en": title_en,
                "title_zh": title_zh,
                "abstract_en": abstract_en,
                "abstract_zh": abstract_zh,
                "url": p.get("link", "")
            })

        email_body = self.builder.build(results)
        return email_body
