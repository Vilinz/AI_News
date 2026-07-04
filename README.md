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

- `GLM_API_KEY`: GLM 模型 API 密钥
- `EMAIL_FROM`: 发件邮箱
- `EMAIL_PASSWORD`: 邮箱密码/授权码
- `EMAIL_TO`: 收件邮箱
- `EMAIL_SERVER`: SMTP 服务器地址（如 smtp.gmail.com）
- `EMAIL_PORT`: SMTP 端口（如 587）