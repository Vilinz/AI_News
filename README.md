# 每日科技/AI 热点推送服务

通过 GitHub Actions 定时运行，支持多种 AI 模型生成摘要并推送每日热点到邮箱。

## 功能

- 每日科技热点
- 每日 AI 热点
- GitHub 热门项目
- 今日头条（无链接版本）
- 支持多种 AI 模型（GLM、OpenAI 等）

## 数据源

### 科技热点 (RSS)
- The Verge
- TechCrunch
- 36氪
- 虎嗅
- InfoQ
- V2EX

### AI 热点 (RSS + 爬虫)
- AI News
- OpenAI Blog
- 量子位 (qbitai.com)
- 机器之心 (jiqizhixin.com)

### GitHub 热门
- GitHub Trending

## 配置

### 必需配置

在 GitHub Secrets 中设置以下必需参数：

| Secret | 说明 | 示例 |
|--------|------|------|
| `API_KEY` | AI 模型 API 密钥 | `sk-xxx` 或 `glm-xxx` |
| `EMAIL_FROM` | 发件邮箱 | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | 邮箱授权码 | `your_app_password` |
| `EMAIL_TO` | 收件邮箱 | `recipient@example.com` |

### 可选配置

| Secret | 默认值 | 说明 |
|--------|--------|------|
| `MODEL` | `glm-4-flash` | 使用的模型名称 |
| `API_BASE_URL` | `https://openrouter.ai` | API 基础 URL |
| `MAX_TOKENS` | `20000` | 最大生成 token 数 |
| `TIMEOUT` | `60` | 请求超时时间（秒） |
| `MAX_RETRIES` | `3` | 最大重试次数 |
| `MAX_TECH_NEWS` | `10` | 科技新闻最大数量 |
| `MAX_AI_NEWS` | `10` | AI 新闻最大数量（含 RSS + 爬虫） |
| `MAX_GITHUB_REPOS` | `10` | GitHub 项目最大数量 |
| `EMAIL_USE_TLS` | `true` | 是否启用 TLS |

### 自动检测的邮箱配置

系统会根据发件邮箱自动配置 SMTP 服务器和端口：

| 邮箱类型 | SMTP 服务器 | 端口 | 协议 |
|---------|-------------|------|------|
| Gmail | smtp.gmail.com | 587 | TLS |
| QQ 邮箱 | smtp.qq.com | 465 | SSL |
| 163 邮箱 | smtp.163.com | 465 | SSL |
| 126 邮箱 | smtp.126.com | 465 | SSL |
| Outlook | smtp-mail.outlook.com | 587 | TLS |
| Hotmail | smtp-mail.outlook.com | 587 | TLS |

其他邮箱默认使用 Gmail 配置。

### 兼容性

为向后兼容，仍支持以下旧环境变量名：
- `GLM_API_KEY` → `API_KEY`
- `GLM_MODEL` → `MODEL`
- `GLM_BASE_URL` → `API_BASE_URL`

### 邮件内容格式

包含以下章节：
1. 每日科技热点（含链接）
2. 每日 AI 热点（含链接）
3. GitHub 热门项目（含链接）
4. 今日头条（无链接版，包含精选内容）

今日头条内容包括：
- 科技热点：精选3条
- AI热点：精选2条
- GitHub热门：精选2条

### 支持的邮箱

| 邮箱 | SMTP 服务器 | 端口 |
|------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| QQ 邮箱 | smtp.qq.com | 465 |
| 163 邮箱 | smtp.163.com | 465 |
| 126 邮箱 | smtp.126.com | 465 |
| Outlook | smtp-mail.outlook.com | 587 |

其他邮箱建议手动配置 `EMAIL_SERVER` 和 `EMAIL_PORT`。

### 模型支持

本项目支持兼容 OpenAI API 格式的所有模型，包括：
- GLM 系列（智谱 AI）
- GPT 系列（OpenAI）
- Claude 系列（Anthropic）
- 其他兼容模型

只需设置正确的 `API_KEY` 和 `API_BASE_URL` 即可。