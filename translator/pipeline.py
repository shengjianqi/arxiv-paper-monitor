# translator/pipeline.py
from .local_translator import AcademicTranslator

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator()

    def process(self, papers):
        if not papers:
            return ""

        texts = []
        for paper in papers:
            text_to_translate = f"Title:\n{paper['title']}\nAbstract:\n{paper['abstract']}"
            texts.append(text_to_translate)

        combined_text = "\n\n---\n\n".join(texts)
        return self.translator.safe_translate(combined_text)
