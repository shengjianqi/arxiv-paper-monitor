# translator/pipeline.py
from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator()
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        papers_raw: arxiv_fetcher 返回的论文列表
        结构示例:
        [
            {
                "title": "...",
                "abstract": "...",
                "pdf_url": "...",
                "arxiv_url": "..."
            }
        ]
        """
        results = []

        for p in papers_raw:
            title_en = p.get("title", "")
            abstract_en = p.get("abstract", "")

            title_zh = self.translator.safe_translate(title_en)
            abstract_zh = self.translator.safe_translate(abstract_en)

            results.append({
                "title_en": title_en,
                "title_zh": title_zh,
                "abstract_en": abstract_en,
                "abstract_zh": abstract_zh,
                "url": p.get("arxiv_url", "")
            })

        email_body = self.builder.build(results)
        return email_body
