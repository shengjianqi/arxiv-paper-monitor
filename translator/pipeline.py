# translator/pipeline.py
from .llm_translator import AcademicTranslator  # ✅ 相对导入

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator(max_wait=2.0)  # 每次请求最大间隔2秒

    def process(self, papers):
        """
        将所有论文合并为一次请求翻译，减少429。
        """
        if not papers:
            return ""

        # 合并所有论文标题+摘要
        texts = []
        for paper in papers:
            text_to_translate = f"Title:\n{paper['title']}\nAbstract:\n{paper['abstract']}"
            texts.append(text_to_translate)

        combined_text = "\n\n---\n\n".join(texts)
        return self.translator.safe_translate(combined_text)
