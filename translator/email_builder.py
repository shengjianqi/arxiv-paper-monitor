# translator/email_builder.py

from datetime import datetime

class TranslationEmailBuilder:

    def build(self, papers):
        """
        papers: list of dict
        each dict:
        {
            "title_en": "...",
            "title_zh": "...",
            "abstract_en": "...",
            "abstract_zh": "...",
            "url": "..."
        }
        """

        date_str = datetime.now().strftime("%Y-%m-%d")

        lines = []
        lines.append(f"📌 arXiv Daily Digest — 中文翻译版 ({date_str})\n")
        lines.append("="*80 + "\n")

        for i, p in enumerate(papers, 1):
            lines.append(f"【{i}】论文标题\n")
            lines.append(f"英文：{p['title_en']}\n")
            lines.append(f"中文：{p['title_zh']}\n\n")

            lines.append("Abstract (English):\n")
            lines.append(p["abstract_en"] + "\n\n")

            lines.append("摘要（中文翻译）：\n")
            lines.append(p["abstract_zh"] + "\n\n")

            if p.get("url"):
                lines.append(f"arXiv链接：{p['url']}\n")

            lines.append("-"*80 + "\n")

        return "\n".join(lines)
