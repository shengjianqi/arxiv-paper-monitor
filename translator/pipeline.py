# translator/pipeline.py

import time
import openai
from translator.email_builder import TranslationEmailBuilder

# ----------------------------
# 安全翻译函数，带重试机制
# ----------------------------
def safe_translate(messages, model="gpt-3.5-turbo", max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            # 返回生成的内容
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            wait = 2 ** retries
            print(f"Rate limit exceeded, retrying in {wait}s...")
            time.sleep(wait)
            retries += 1
        except openai.error.APIError as e:
            wait = 2 ** retries
            print(f"API error ({e}), retrying in {wait}s...")
            time.sleep(wait)
            retries += 1
        except openai.error.Timeout:
            wait = 2 ** retries
            print(f"Timeout, retrying in {wait}s...")
            time.sleep(wait)
            retries += 1
    raise Exception("Exceeded retry limit for translation")

# ----------------------------
# 翻译处理流水线
# ----------------------------
class TranslationPipeline:

    def __init__(self):
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        papers_raw: 来自 arxiv 抓取模块的数据
        结构示例:
        [
            {
                "title": "...",
                "summary": "...",
                "link": "https://arxiv.org/abs/xxxx"
            }
        ]
        """

        results = []

        for p in papers_raw:
            title_en = p.get("title", "")
            abstract_en = p.get("summary", "")

            # 翻译标题
            title_zh = safe_translate([
                {"role": "user", "content": f"请将以下英文标题翻译成中文:\n{title_en}"}
            ])

            # 翻译摘要
            abstract_zh = safe_translate([
                {"role": "user", "content": f"请将以下英文摘要翻译成中文:\n{abstract_en}"}
            ])

            results.append({
                "title_en": title_en,
                "title_zh": title_zh,
                "abstract_en": abstract_en,
                "abstract_zh": abstract_zh,
                "url": p.get("link", "")
            })

        # 构建邮件内容
        email_body = self.builder.build(results)
        return email_body
