# translator/local_translator.py
from transformers import MarianMTModel, MarianTokenizer

class AcademicTranslator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-en-zh"):
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def batch_translate(self, texts, batch_size=8):
        translations = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            tokens = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
            translated = self.model.generate(**tokens, max_new_tokens=512)
            decoded = [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated]
            translations.extend(decoded)
        return translations
