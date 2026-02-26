import os
from datetime import datetime
import logging

from config import Config
from arxiv_fetcher import ArxivFetcher
from email_sender import EmailSender

from translator.pipeline import TranslationPipeline
from config import Config

def run():
    papers = fetch_papers()
    pipeline = TranslationPipeline()  # 不再传 api_key
    translated_body = pipeline.process(papers)
    print(translated_body)

if __name__ == "__main__":
    run()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ArxivDailyDigest:
    def __init__(self):
        self.fetcher = ArxivFetcher()
        self.email_sender = EmailSender()

    def run(self, test_mode=False):
        logger.info("=" * 60)
        logger.info(f"开始执行Arxiv论文抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            days_back = 0 if test_mode else 1
            papers = self.fetcher.fetch_recent_papers(days_back=days_back)

            summaries = []
            if papers:
                summaries = [self.fetcher.generate_summary(p) for p in papers]
                logger.info(f"找到 {len(papers)} 篇相关论文")
            else:
                logger.info("今日没有找到相关论文")

            # 发送英文摘要
            success = self.email_sender.send_digest(papers, summaries)

            if not success:
                logger.error("❌ 英文摘要邮件发送失败")
                return

            logger.info("✅ 英文摘要邮件发送成功")

            # ===== 中文翻译邮件 =====
            if papers:
                logger.info(f"📘 翻译模块触发，论文数 = {len(papers)}")

                from translator.pipeline import TranslationPipeline
                pipeline = TranslationPipeline(api_key=Config.OPENAI_API_KEY)

                translated_body = pipeline.process(papers)

                zh_success = self.email_sender.send_email(
                    subject="arXiv Daily Digest — 中文翻译版",
                    body=translated_body
                )

                if zh_success:
                    logger.info("✅ 中文翻译邮件发送成功")
                else:
                    logger.error("❌ 中文翻译邮件发送失败")

        except Exception as e:
            logger.exception(f"任务执行失败: {e}")

        logger.info("=" * 60)

    def run_once(self, test_mode=False):
        logger.info("🚀 启动单次任务模式（GitHub Actions）")
        self.run(test_mode=test_mode)
        logger.info("📤 单次任务执行完毕，进程将退出")


def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return

    digest = ArxivDailyDigest()

    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("RUN_MODE") == "ci":
        logger.info("检测到CI/CD环境，使用单次运行模式")
        digest.run_once(test_mode=False)
    else:
        digest.run(test_mode=True)


if __name__ == "__main__":
    main()
