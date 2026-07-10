import arxiv
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

class ArxivFetcher:
    def __init__(self):
        # 使用较小的 page_size 和较长的延迟来避免触发 arXiv 限速
        self.client = arxiv.Client(
            page_size=30,        # 每次API请求只取30条（默认100）
            delay_seconds=5.0,   # 请求间延迟5秒（默认3秒）
            num_retries=5        # 最多重试5次（默认3次）
        )
        self.keywords = Config.SEARCH_KEYWORDS

    def fetch_recent_papers(self, days_back: int = 1) -> List[Dict]:
        """
        获取最近几天的论文

        Args:
            days_back: 回溯天数，默认为1（获取过去24小时的）
        """
        try:
            # 计算日期范围（使用UTC时间）
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_back)

            # 构建搜索查询
            # 使用 all: 字段（搜索标题+摘要+作者），不用 submittedDate API过滤
            # 因为 submittedDate 过滤可能因格式问题导致0结果
            keyword_terms = []
            for kw in self.keywords:
                kw = kw.strip()
                if ' ' in kw:
                    keyword_terms.append(f'all:"{kw}"')
                else:
                    keyword_terms.append(f'all:{kw}')

            keyword_query = " OR ".join(keyword_terms)

            logger.info(f"搜索关键词: {self.keywords}")
            logger.info(f"搜索查询: {keyword_query}")
            logger.info(f"日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")

            # 搜索论文
            search = arxiv.Search(
                query=keyword_query,
                max_results=Config.MAX_RESULTS * 2,  # 多获取一些以便日期过滤
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            # 带重试的搜索（处理 HTTP 429 限速）
            max_attempts = 4
            for attempt in range(max_attempts):
                try:
                    papers = []
                    for result in self.client.results(search):
                        pub_date = result.published
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)

                        if pub_date < start_date:
                            logger.debug(f"跳过旧论文: {result.title[:50]}...")
                            continue

                        paper = {
                            'id': result.get_short_id(),
                            'title': result.title,
                            'authors': [author.name for author in result.authors],
                            'abstract': result.summary,
                            'pdf_url': result.pdf_url,
                            'published': pub_date.strftime('%Y-%m-%d %H:%M'),
                            'primary_category': result.primary_category,
                            'categories': result.categories,
                            'arxiv_url': result.entry_id,
                        }
                        papers.append(paper)
                        logger.info(f"✅ 找到论文: {paper['title'][:80]}... ({pub_date.strftime('%Y-%m-%d')})")

                    logger.info(f"共找到 {len(papers)} 篇相关论文 (过去{days_back}天内)")
                    return papers

                except arxiv.HTTPError as e:
                    if '429' in str(e):
                        wait_time = (attempt + 1) * 30  # 30s, 60s, 90s, 120s
                        logger.warning(f"arXiv API 限速 (HTTP 429)，等待 {wait_time} 秒后重试 (第{attempt+1}/{max_attempts}次)...")
                        time.sleep(wait_time)
                        continue
                    raise
                except arxiv.UnexpectedEmptyPageError:
                    # 空页面是正常的，说明没有更多结果
                    break

            logger.info(f"所有重试后，共找到 {len([])} 篇相关论文")
            return []

        except Exception as e:
            logger.error(f"获取论文失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def generate_summary(self, paper: Dict) -> str:
        """生成论文的中文摘要"""
        title = paper['title']
        abstract = paper['abstract']

        summary_lines = [
            "=" * 60,
            f"📄 标题: {title}",
            "",
            f"👥 作者: {', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}",
            f"📅 发布时间: {paper['published']}",
            f"📚 分类: {paper['primary_category']}",
            "",
            "📝 摘要:",
            self._truncate_text(abstract, 800) + ("..." if len(abstract) > 800 else ""),
            "",
            "🔗 链接:",
            f"PDF: {paper['pdf_url']}",
            f"Arxiv: {paper['arxiv_url']}",
            "=" * 60,
            ""
        ]

        return "\n".join(summary_lines)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0]
