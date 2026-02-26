# translator/pipeline.py
from translator.llm_translator import AcademicTranslator

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator(model="gpt-3.5-turbo")

    def process(self, papers):
        translated_results = []
        for paper in papers:
            title_zh = self.translator.safe_translate(paper['title'])
            abstract_zh = self.translator.safe_translate(paper['abstract'])
            translated_results.append(
                f"📄 {title_zh}\n📝 {abstract_zh}\n{'-'*40}\n"
            )
        return "\n".join(translated_results)
