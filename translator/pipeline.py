# translator/pipeline.py

import logging
import time
from typing import List, Dict
from translator.llm_translator import AcademicTranslator
from config import Config

logger = logging.getLogger(__name__)

class TranslationPipeline:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        # 直接使用 Config.OPENAI_API_KEY，不再传 api_key
        self.translator = AcademicTranslator(
            api_key=Config.OPENAI_API_KEY,
            model=model
        )

    def process(self, papers: List[Dict]) -> str:
        """
        批量翻译论文标题+摘要，返回拼接的中文文本
        """
        if not papers:
            return ""

        # 构建批量文本
        texts_to_translate = []
        for i, paper in enumerate(papers, start=1):
            text = (
                f"论文 {i}:\n"
                f"标题: {paper['title']}\n"
                f"摘要: {paper['abstract']}\n"
                f"作者: {', '.join(paper['authors'])}\n"
            )
            texts_to_translate.append(text)

        # 拼接为一个大文本，一次性翻译
        batch_text = "\n\n".join(texts_to_translate)

        translated_text = self._safe_translate(batch_text)
        return translated_text

    def _safe_translate(self, text: str, max_retries: int = 5) -> str:
        """带指数退避的安全翻译"""
        retry = 0
        wait = 1  # 初始等待 1 秒

        while retry < max_retries:
            try:
                result = self.translator.translate(text)
                return result
            except Exception as e:
                msg = str(e)
                if "429" in msg or "RateLimit" in msg:
                    retry += 1
                    logger.info(f"⚠️ 遇到速率限制，等待 {wait} 秒重试 ({retry}/{max_retries})")
                    time.sleep(wait)
                    wait *= 2  # 指数退避
                else:
                    logger.error(f"❌ 翻译失败: {e}")
                    return "[Translation Failed]"
        logger.error("❌ 多次重试后翻译仍失败")
        return "[Translation Failed]"
