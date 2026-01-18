# 📬 Arxiv 论文每日摘要自动化系统

一个部署在 GitHub Actions 上的全自动工具，每天定时从 arXiv 抓取“里德堡原子”（可配置）相关的最新论文，并生成中文摘要发送到你的邮箱。

---

## ✨ 核心功能

*   **定时抓取**：每天在指定时间自动查询 arXiv。
*   **中文摘要**：自动生成论文的简明中文摘要。
*   **邮件推送**：将摘要结果（无论文时发送通知）发送到你的邮箱。
*   **灵活配置**：通过 `.env` 文件和 GitHub Secrets 轻松修改所有参数。
*   **无需运维**：基于 GitHub Actions，零服务器成本。

---

## ⚙️ 如何配置（两个关键步骤）

你的配置信息通过两种方式管理：
1.  **`.env` 文件**：用于本地测试和存放非敏感配置（如关键词）。
2.  **GitHub Secrets**：用于云端安全运行，存放敏感信息（如邮箱密码）。

### 第一步：配置 `.env` 文件（用于修改关键词和基础设置）

在项目根目录创建或修改 `.env` 文件，它是你所有配置的入口。

```ini
# ============ 【必填】邮箱配置（用于本地测试）============
# 你的QQ邮箱地址
EMAIL_SENDER=your_email@qq.com
# 你的QQ邮箱16位SMTP授权码（不是登录密码）
EMAIL_PASSWORD=your_16_digit_auth_code
# 收件人邮箱（多个邮箱用英文分号 ; 隔开）
RECIPIENT_EMAIL=receiver1@example.com;receiver2@example.com

# ============ 【必改】Arxiv 搜索配置 ============
# 搜索关键词，用英文逗号分隔。例如，想同时监控“量子计算”和“超导”
SEARCH_KEYWORDS=Rydberg atom, Rydberg state, 里德堡原子

# ============ 【选填】其他运行参数 ============
# 每次搜索返回的最大论文数量
MAX_RESULTS=20
# 程序运行时区（保持 Asia/Shanghai 即可）
TZ=Asia/Shanghai
