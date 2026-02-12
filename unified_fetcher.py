from arxiv_fetcher import ArxivFetcher
from config import Config

class UnifiedPaperFetcher:
    def __init__(self):
        self.arxiv = ArxivFetcher()
        self.prl = None   # PRL 模块暂时禁用

    def fetch_all(self):
        papers = []
        papers.extend(self.arxiv.fetch())
        return papers
