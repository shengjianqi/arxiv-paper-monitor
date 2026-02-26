# translator/pipeline.py
from .llm_translator import AcademicTranslator  # ✅ 使用相对导入

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator()

    def process(self, papers):
        """批量处理所有论文，标题+摘要合并"""
        translated_texts = []

        for paper in papers:
            text_to_translate = f"Title:\n{paper['title']}\nAbstract:\n{paper['abstract']}"
            zh = self.translator.safe_translate(text_to_translate)
            translated_texts.append(zh)

        return "\n\n".join(translated_texts)
