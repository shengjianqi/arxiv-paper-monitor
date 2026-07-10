"""
ArXiv 论文抓取器 — 直接使用 HTTP 请求 + feedparser
避免 arxiv 库的内部重试机制与 arXiv API 限速策略冲突
"""
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
import time
import urllib.parse
from config import Config

logger = logging.getLogger(__name__)

# arXiv API 基础URL
ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivFetcher:
    def __init__(self):
        self.keywords = Config.SEARCH_KEYWORDS
        self.max_results = Config.MAX_RESULTS

    def _build_query(self) -> str:
        """构建 arXiv API 搜索查询"""
        terms = []
        for kw in self.keywords:
            kw = kw.strip()
            if ' ' in kw:
                terms.append(f'all:"{kw}"')
            else:
                terms.append(f'all:{kw}')
        return " OR ".join(terms)

    def _search_request(self, query: str, start: int, max_results: int) -> Optional[bytes]:
        """
        发送单次 arXiv API 请求，带限速重试
        返回原始 XML 内容，或 None（失败时）
        """
        params = {
            'search_query': query,
            'start': start,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
        }
        url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

        # 最多重试5次，指数退避
        for attempt in range(5):
            try:
                resp = requests.get(
                    url,
                    timeout=30,
                    headers={
                        'User-Agent': 'ArxivDailyDigest/1.0 (mailto:arxiv-digest@example.com)'
                    }
                )

                if resp.status_code == 200:
                    return resp.content

                if resp.status_code == 429:
                    wait = min((attempt + 1) * 20, 120)  # 20s, 40s, 60s, 80s, 120s
                    logger.warning(f"arXiv API 限速 (HTTP 429)，等待 {wait}s 后重试 (第{attempt+1}/5次)...")
                    time.sleep(wait)
                    continue

                if resp.status_code == 503:
                    wait = min((attempt + 1) * 10, 60)
                    logger.warning(f"arXiv API 暂时不可用 (HTTP 503)，等待 {wait}s 后重试...")
                    time.sleep(wait)
                    continue

                logger.error(f"arXiv API 返回意外状态码: {resp.status_code}")
                return None

            except requests.RequestException as e:
                wait = min((attempt + 1) * 10, 60)
                logger.warning(f"网络请求失败: {e}，等待 {wait}s 后重试...")
                time.sleep(wait)
                continue

        logger.error("arXiv API 请求失败：重试次数已用完")
        return None

    def _parse_response(self, xml_content: bytes, start_date: datetime, end_date: datetime) -> List[Dict]:
        """解析 arXiv API 的 Atom XML 响应"""
        feed = feedparser.parse(xml_content)
        papers = []

        for entry in feed.entries:
            try:
                # 解析发布日期
                published_str = entry.get('published', '')
                if published_str:
                    # arXiv dates are like: 2026-07-08T17:59:59Z
                    pub_date = datetime.strptime(published_str[:10], '%Y-%m-%d')
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                else:
                    continue

                # 日期过滤
                if pub_date < start_date:
                    continue

                # 提取作者
                authors = []
                for author in entry.get('authors', []):
                    name = author.get('name', '')
                    if name:
                        authors.append(name)

                # 提取分类
                categories = []
                for tag in entry.get('tags', []):
                    term = tag.get('term', '')
                    if term:
                        categories.append(term)

                # 提取链接
                pdf_url = ''
                arxiv_url = entry.get('link', '')
                for link in entry.get('links', []):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href', '')
                    elif link.get('rel') == 'alternate':
                        arxiv_url = link.get('href', '')

                # ID 简化
                arxiv_id = entry.get('id', '').split('/')[-1]
                # 移除版本号 (v1, v2, etc.)
                if 'v' in arxiv_id:
                    arxiv_id = arxiv_id.rsplit('v', 1)[0]

                paper = {
                    'id': arxiv_id,
                    'title': entry.get('title', 'Unknown').strip(),
                    'authors': authors,
                    'abstract': entry.get('summary', '').strip(),
                    'pdf_url': pdf_url,
                    'published': pub_date.strftime('%Y-%m-%d %H:%M'),
                    'primary_category': categories[0] if categories else 'unknown',
                    'categories': categories,
                    'arxiv_url': arxiv_url,
                }
                papers.append(paper)

            except Exception as e:
                logger.debug(f"解析论文条目失败: {e}")
                continue

        return papers

    def fetch_recent_papers(self, days_back: int = 1) -> List[Dict]:
        """
        获取最近几天的论文

        Args:
            days_back: 回溯天数，默认为1（获取过去24小时的）
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_back)

            query = self._build_query()
            logger.info(f"搜索关键词: {self.keywords}")
            logger.info(f"arXiv 查询: {query}")
            logger.info(f"日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")

            all_papers = []
            start = 0
            batch_size = 30  # 每页请求30条（避免触发限速）

            # 分页获取，最多3页
            for page in range(3):
                logger.info(f"获取第 {page+1} 页 (start={start}, max_results={batch_size})...")

                # 请求间延迟（避免触发限速）
                if page > 0:
                    time.sleep(10)

                xml_content = self._search_request(query, start, batch_size)
                if xml_content is None:
                    logger.warning(f"第 {page+1} 页请求失败，停止获取更多页")
                    break

                papers = self._parse_response(xml_content, start_date, end_date)

                if not papers:
                    logger.info(f"第 {page+1} 页没有符合日期条件的论文，停止翻页")
                    break

                all_papers.extend(papers)
                logger.info(f"第 {page+1} 页找到 {len(papers)} 篇论文")

                # 如果返回的论文数少于请求数，说明已到末尾
                if len(papers) < batch_size:
                    break

                start += batch_size

                # 如果已经达到 MAX_RESULTS，停止
                if len(all_papers) >= self.max_results:
                    break

            # 限制总结果数
            all_papers = all_papers[:self.max_results]

            for p in all_papers:
                logger.info(f"✅ 找到论文: {p['title'][:80]}... ({p['published'][:10]})")

            logger.info(f"共找到 {len(all_papers)} 篇相关论文 (过去{days_back}天内)")
            return all_papers

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
