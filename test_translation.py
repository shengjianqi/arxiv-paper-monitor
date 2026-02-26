from translator.pipeline import TranslationPipeline
from config import Config

# 构造一篇假论文
papers = [
    {
        "title": "Quantum-enhanced imaging beyond the diffraction limit",
        "authors": ["A. Einstein", "N. Bohr"],
        "abstract": "We propose a novel quantum imaging protocol that surpasses the classical diffraction limit using entangled photon pairs and spatial mode engineering.",
        "published": "2026-02-26",
        "primary_category": "quant-ph",
        "pdf_url": "https://arxiv.org/pdf/0000.00000.pdf",
        "arxiv_url": "https://arxiv.org/abs/0000.00000"
    }
]

print("=" * 60)
print("OPENAI_API_KEY loaded:", bool(Config.OPENAI_API_KEY))

pipeline = TranslationPipeline(api_key=Config.OPENAI_API_KEY)

print("Starting translation test...")

result = pipeline.process(papers)

print("=" * 60)
print("Translation result:")
print(result)
print("=" * 60)
