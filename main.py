# main.py - GitHub Actions 适配 + 中英文双邮件版本
import os
from datetime import datetime
import logging

from config import Config
from arxiv_fetcher import ArxivFetcher
from email_sender import EmailSender

# ================= 日志配置 =================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# ================= 主逻辑类 =================

class ArxivDailyDigest:
    def __init__(self):
        self.fetcher = ArxivFetcher()
        self.email_sender = EmailSender()

    def run(self, test_mode=False):
        """执行一次完整任务流程"""
        logger.info("=" * 60)
        logger.info(f"开始执行任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 1. 获取论文
            days_back = 0 if test_mode else 1
            papers = self.fetcher.fetch_recent_papers(days_back=days_back)

            # 2. 生成英文摘要
            summaries = []
            if papers:
                summaries = [
                    self.fetcher.generate_summary(paper)
                    for paper in papers
                ]
                logger.info(f"找到 {len(papers)} 篇相关论文")
            else:
                logger.info("今日没有找到相关论文")

            # 3. 发送英文摘要邮件
            success = self.email_sender.send_digest(papers, summaries)

            if not success:
                logger.error("❌ 英文摘要邮件发送失败")
                return

            if papers:
                logger.info(f"✅ 英文摘要邮件发送成功：{len(papers)} 篇论文")
            else:
                logger.info("✅ 已发送『今日无新论文』英文通知")

            # 4. 发送中文翻译邮件（仅当存在论文时）
            if papers:
                try:
                    logger.info("📘 开始生成中文翻译邮件...")

                    from translator.pipeline import TranslationPipeline

                    pipeline = TranslationPipeline(
                        api_key=Config.OPENAI_API_KEY
                    )

                    translated_email_body = pipeline.process(papers)

                    zh_success = self.email_sender.send_email(
                        subject="arXiv Daily Digest — 中文翻译版",
                        body=translated_email_body
                    )

                    if zh_success:
                        logger.info("✅ 中文翻译邮件发送成功")
                    else:
                        logger.error("❌ 中文翻译邮件发送失败")

                except Exception as e:
                    logger.exception(f"❌ 中文翻译邮件处理异常: {e}")

        except Exception as e:
            logger.exception(f"任务执行失败: {e}")

        logger.info("=" * 60)

    def run_once(self, test_mode=False):
        """CI/CD 单次执行模式"""
        logger.info("🚀 启动单次运行模式（GitHub Actions）")
        self.run(test_mode=test_mode)
        logger.info("📤 单次任务执行完毕，进程将退出")


# ================= 入口函数 =================

def main():
    """主入口，根据环境自动判断运行模式"""

    # 配置校验
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return

    digest = ArxivDailyDigest()

    # 结构安全断言（防止缩进错误）
    assert hasattr(digest, "run_once"), "run_once 方法未正确加载，请检查缩进"

    # CI / GitHub Actions 环境
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("RUN_MODE") == "ci":
        logger.info("检测到CI/CD环境，使用单次运行模式")
        digest.run_once(test_mode=False)
    else:
        if Config.TEST_MODE:
            logger.info("本地测试模式运行")
            digest.run(test_mode=True)
        else:
            logger.info("本地直接运行一次")
            digest.run_once(test_mode=False)


if __name__ == "__main__":
    main()
