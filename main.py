# main.py
import os
from datetime import datetime
import logging

from config import Config
from arxiv_fetcher import ArxivFetcher
from email_sender import EmailSender
from translator.pipeline import TranslationPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArxivDailyDigest:
    def __init__(self):
        self.fetcher = ArxivFetcher()
        self.email_sender = EmailSender()
        self.translator = TranslationPipeline()

    def run(self, test_mode=False):
        logger.info("="*60)
        logger.info(f"开始执行Arxiv论文抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            days_back = 0 if test_mode else 1
            papers = self.fetcher.fetch_recent_papers(days_back=days_back)
            if not papers:
                logger.info("今日没有找到相关论文")
                return

            # 英文摘要
            summaries = [self.fetcher.generate_summary(p) for p in papers]
            self.email_sender.send_email("arXiv Daily Digest — English", "\n\n".join(summaries))
            logger.info("✅ 英文摘要邮件发送成功")

            # 中文翻译邮件
            translated_body = self.translator.process(papers)
            self.email_sender.send_email("arXiv Daily Digest — 中文翻译版", translated_body)
            logger.info("✅ 中文翻译邮件发送成功")

        except Exception as e:
            logger.exception(f"任务执行失败: {e}")
        logger.info("="*60)

    def run_once(self, test_mode=False):
        logger.info("🚀 启动单次任务模式")
        self.run(test_mode=test_mode)

def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return

    digest = ArxivDailyDigest()
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("RUN_MODE") == "ci":
        digest.run_once(test_mode=False)
    else:
        digest.run(test_mode=True)

if __name__ == "__main__":
    main()
