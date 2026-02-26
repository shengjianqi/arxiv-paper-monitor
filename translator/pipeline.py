# translator/pipeline.py
from .local_translator import AcademicTranslator

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator()

    def process(self, papers):
        # 提取所有摘要
        abstracts = [p['abstract'] for p in papers]
        zh_abstracts = self.translator.batch_translate(abstracts)

        # 保存翻译
        for paper, zh in zip(papers, zh_abstracts):
            paper['zh_abstract'] = zh

        return self.format_html(papers)

    def format_html(self, papers):
        html = """
        <html>
        <head>
        <style>
        body { font-family: Helvetica, sans-serif; line-height: 1.5; }
        .paper { border-bottom:1px solid #ddd; padding:10px 0; }
        .title { font-weight:bold; font-size:16px; color:#003366; }
        .authors { font-style:italic; color:#555; }
        .abstract { margin:8px 0; color:#333; }
        .links { font-size:14px; }
        </style>
        </head>
        <body>
        <h2>arXiv Daily Digest — 中文翻译版</h2>
        """
        for p in papers:
            html += f"""
            <div class="paper">
              <div class="title">{p['title']}</div>
              <div class="authors">Authors: {', '.join(p['authors'])}</div>
              <div class="abstract">{p['zh_abstract']}</div>
              <div class="links">
                <a href="{p['pdf_url']}">PDF</a> |
                <a href="{p['arxiv_url']}">arXiv</a>
              </div>
            </div>
            """
        html += "</body></html>"
        return html
