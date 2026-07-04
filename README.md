# 每日科技/AI 热点推送服务

通过 GitHub Actions 定时运行，使用 GLM 模型生成摘要并推送每日热点到邮箱。

## 功能

- 每日科技热点
- 每日 AI 热点
- GitHub 热门项目

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

在 GitHub Secrets 中设置：

| Secret | 说明 | 示例 |
|--------|------|------|
| `GLM_API_KEY` | GLM 模型 API 密钥 | - |
| `EMAIL_FROM` | 发件邮箱（自动检测 SMTP） | `your_email@qq.com` |
| `EMAIL_PASSWORD` | 邮箱授权码 | - |
| `EMAIL_TO` | 收件邮箱 | - |

### 支持自动检测的邮箱

| 邮箱 | SMTP 服务器 | 端口 |
|------|-------------|------|
| QQ 邮箱 | smtp.qq.com | 465 |
| 163 邮箱 | smtp.163.com | 465 |
| 126 邮箱 | smtp.126.com | 465 |
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |

其他邮箱需手动配置 `EMAIL_SERVER` 和 `EMAIL_PORT`。