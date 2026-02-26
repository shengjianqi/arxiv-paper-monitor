# translator/pipeline.py

import time
import openai
from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder


def safe_translate(messages):
    """
    安全调用 OpenAI API 翻译文本，带重试机制
    messages: List[dict] [{"role": "user", "content": "..."}]
    返回: 模型生成的文本
    """
    retries = 0
    while retries < 5:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # 使用 GPT-3.5
                messages=messages
            )
            return response.choices[0].message.content
        except openai.error.OpenAIError as e:  # 新版统一异常
            wait = 2 ** retries
            print(f"OpenAI API error: {e}, retrying in {wait}s...")
            time.sleep(wait)
            retries += 1
    raise Exception("Exceeded retry limit")


class TranslationPipeline:

    def __init__(self, api_key):
        """
        初始化翻译管线
        """
        openai.api_key = api_key
        self.translator = AcademicTranslator(api_key)
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        处理论文列表，翻译标题和摘要，并生成邮件内容
        papers_raw: list of dicts
        示例:
        [
            {
                "title": "Paper title",
                "abstract": "Paper abstract",
                "link": "https://arxiv.org/abs/xxxx"
            },
            ...
        ]
        返回: 邮件正文字符串
        """
        results = []

        for p in papers_raw:
            title_en = p.get("title", "")
            abstract_en = p.get("abstract", "")

            # 调用安全翻译
            title_zh = self.translator.safe_translate([
                {"role": "user", "content": f"请将以下英文标题翻译成中文:\n{title_en}"}
            ])
            abstract_zh = self.translator.safe_translate([
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
