from transformers import MarianMTModel, MarianTokenizer
import logging

logger = logging.getLogger(__name__)

class AcademicTranslator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-en-zh"):
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        lines = text.split("\n")
        translations = []
        for line in lines:
            if not line.strip():
                translations.append("")
                continue
            tokens = self.tokenizer(line, return_tensors="pt", truncation=True)
            translated = self.model.generate(**tokens, max_length=512)
            translated_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
            translations.append(translated_text)
        return "\n".join(translations)

    def safe_translate(self, text: str):
        try:
            return self.translate(text)
        except Exception as e:
            logger.error(f"[Translator Error] {e}")
            return "[Translation Failed]"
