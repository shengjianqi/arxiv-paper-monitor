# translator/pipeline.py

import time
import openai
from translator.llm_translator import AcademicTranslator
from translator.email_builder import TranslationEmailBuilder

# 设置 API Key
# 注意：可以从环境变量或者配置文件读取
# openai.api_key = "YOUR_API_KEY"

def safe_translate(prompt, model="gpt-3.5-turbo", retries=5):
    """
    使用 OpenAI Chat API 翻译文本，带指数退避重试
    prompt: str 待翻译文本
    """
    wait = 1
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            # 返回模型回复内容
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error (attempt {attempt+1}): {e}")
            time.sleep(wait)
            wait *= 2
    raise Exception("Translation failed after retries")


class TranslationPipeline:
    """
    翻译流程管道
    """

    def __init__(self):
        self.translator = AcademicTranslator()  # 保留原有翻译类逻辑
        self.builder = TranslationEmailBuilder()

    def process(self, papers_raw):
        """
        papers_raw: list of dict, 结构示例
        [
            {
                "title": "...",
                "summary": "...",
                "link": "https://arxiv.org/abs/xxxx"
            }
        ]
        """
        results = []

        # --- 批量翻译标题 ---
        titles = [p["title"] for p in papers_raw]
        titles_prompt = "请将以下论文标题翻译成中文，并按编号返回，每行格式 '编号. 中文标题':\n" + \
                        "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
        titles_zh_text = safe_translate(titles_prompt)

        # 拆分每行结果
        titles_zh_list = [line.strip().split('.', 1)[1].strip() if '.' in line else line.strip()
                          for line in titles_zh_text.split('\n')]

        # --- 批量翻译摘要 ---
        abstracts = [p.get("abstract", "") for p in papers_raw]
        abstracts_prompt = "请将以下论文摘要翻译成中文，每篇摘要用编号标记，并保持原顺序:\n" + \
                           "\n".join([f"{i+1}. {a}" for i, a in enumerate(abstracts)])
        abstracts_zh_text = safe_translate(abstracts_prompt)

        abstracts_zh_list = [line.strip().split('.', 1)[1].strip() if '.' in line else line.strip()
                             for line in abstracts_zh_text.split('\n')]

        # --- 组合结果 ---
        for idx, paper in enumerate(papers_raw):
            title_zh = titles_zh_list[idx] if idx < len(titles_zh_list) else ""
            abstract_zh = abstracts_zh_list[idx] if idx < len(abstracts_zh_list) else ""
            results.append({
                "title_en": paper["title"],
                "title_zh": title_zh,
                "abstract_en": paper.get("abstract", ""),
                "abstract_zh": abstract_zh,
                "url": paper.get("link", "")
            })

        # --- 构建邮件内容 ---
        email_body = self.builder.build(results)
        return email_body
