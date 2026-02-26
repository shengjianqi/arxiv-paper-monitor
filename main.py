# main.py
import logging
from arxiv_fetcher import ArxivFetcher
from email_sender import EmailSender
from translator.pipeline import TranslationPipeline
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return

    fetcher = ArxivFetcher()
    emailer = EmailSender()
    translator = TranslationPipeline()

    papers = fetcher.fetch_recent_papers(days_back=1)
    if not papers:
        logger.info("今日没有找到论文")
        return

    summaries = [fetcher.generate_summary(p) for p in papers]
    emailer.send_digest(papers, summaries)

    translated_body = translator.process(papers)
    emailer.send_email(subject="arXiv Daily Digest — 中文翻译版", body=translated_body)

if __name__ == "__main__":
    main()
