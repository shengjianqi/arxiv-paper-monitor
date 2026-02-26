# translator/pipeline.py

from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder
import time
from config import Config

class TranslationPipeline:
    def __init__(self):
        # 从 Config 读取 API Key
        self.translator = AcademicTranslator(api_key=Config.OPENAI_API_KEY)
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        papers_raw: arxiv抓取的论文数据列表
        [
            {"title": "...", "summary": "...", "link": "..."}
        ]
        """
        results = []

        for p in papers_raw:
            title_en = str(p.get("title", ""))
            abstract_en = str(p.get("abstract", ""))

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
