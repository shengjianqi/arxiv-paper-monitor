# translator/pipeline.py
from .local_translator import AcademicTranslator
import logging

logger = logging.getLogger(__name__)

class TranslationPipeline:
    def __init__(self):
        self.translator = AcademicTranslator()

    def process(self, papers: list) -> str:
        """
        输入 arxiv papers，返回中文邮件正文
        """
        abstracts = [p['abstract'] for p in papers]
        zh_abstracts = self.translator.batch_translate(abstracts, delay=1.5)

        # 构建HTML正文
        content = ""
        for i, (paper, zh_abs) in enumerate(zip(papers, zh_abstracts), 1):
            authors = ', '.join(paper['authors'][:3]) + ('等' if len(paper['authors']) > 3 else '')
            content += f"""
            <div class="paper">
                <div class="title">📄 论文 #{i}: {paper['title']}</div>
                <div class="meta">
                    👥 作者: {authors}<br>
                    📅 发布时间: {paper['published']} | 📚 分类: {paper['primary_category']}
                </div>
                <div class="abstract">
                    <strong>摘要 (中文):</strong><br>
                    {zh_abs[:500]}...
                </div>
                <div class="links">
                    <a class="link" href="{paper['pdf_url']}">📥 下载PDF</a>
                    <a class="link" href="{paper['arxiv_url']}">🔗 查看原文</a>
                </div>
            </div>
            """
        return content
