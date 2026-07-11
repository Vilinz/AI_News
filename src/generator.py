import os
import requests
import time
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from requests.exceptions import Timeout, RequestException

load_dotenv()


class GLMContentGenerator:
    def __init__(self):
        # 使用全局配置
        self.api_key = config.api_key
        self.base_url = config.api_base_url
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout
        self.max_retries = config.max_retries

    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API生成内容"""
        timeout = self.timeout

        for attempt in range(self.max_retries):
            try:
                print(f"  尝试 {attempt + 1}/{self.max_retries}: 发送请求到 {self.base_url}")
                request_data = {
                    "model": config.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens
                }
                print(f"  请求数据大小: {len(str(request_data))} 字符")

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=config.get_api_headers(),
                    json=request_data,
                    timeout=timeout
                )
                print(f"  响应状态码: {response.status_code}")
                print(f"  响应内容前200字符: {response.text[:200]}")
                response.raise_for_status()
                result = response.json()

                # 根据不同的 API 格式处理响应
                if 'choices' in result:
                    content = result['choices'][0]['message']['content']
                elif 'content' in result:
                    content = result['content']
                elif 'response' in result:
                    content = result['response']
                else:
                    content = str(result)

                return content

            except Timeout as e:
                if attempt < self.max_retries - 1:
                    wait_time = min(2 ** attempt, 4)
                    print(f"请求超时，{wait_time}秒后重试 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"达到最大重试次数，请求超时: {e}")
                    return f"生成失败: 请求超时 (已重试{self.max_retries}次)"

            except RequestException as e:
                print(f"请求失败详情:")
                if e.request is not None:
                    print(f"  - URL: {e.request.url}")
                else:
                    print(f"  - URL: N/A")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"  - 状态码: {e.response.status_code}")
                    print(f"  - 响应内容: {e.response.text[:200]}...")
                else:
                    print(f"  - 状态码: N/A")
                return f"生成失败: {str(e)}"

            except Exception as e:
                print(f"未知错误: {e}")
                return f"生成失败: {str(e)}"

    def generate_toutiao_article(self, topic_title: str) -> str:
        """为单个今日头条热点生成微头条文章"""
        prompt = f"""请针对以下今日头条热点话题，撰写一篇适合发布在今日头条微头条的文章。

热点话题：{topic_title}

要求：
1. 文章字数在500字左右
2. 开头要吸引眼球，可以用反问、感叹或悬念引入
3. 内容要有深度，包括：
   - 事件背景和核心信息
   - 相关分析和解读
   - 个人观点或行业影响
   - 引发读者思考或讨论
4. 语言要生动有趣，接地气，像真人写的
5. 适当使用一些修辞手法，增强可读性
6. 结尾可以抛出问题或观点，引导读者评论互动
7. 不要使用markdown格式，纯文本输出
8. 不要添加任何链接

请直接输出文章内容，不要添加标题或其他说明："""

        print(f"\n  [生成微头条] {topic_title}")
        content = self._call_ai_api(prompt)
        return content

    def generate_summary(self, news_data: Dict) -> str:
        """使用 GLM 生成每日摘要"""
        today = str(datetime.now().date())

        # Build input content (including links)
        tech_section = "\n".join([
            f"- {item['title']} | {item['link']}\n  {item['summary']}"
            for item in news_data['tech_news']
        ])

        ai_section = "\n".join([
            f"- {item['title']} | {item['link']}\n  {item['summary']}"
            for item in news_data['ai_news']
        ])

        github_section = "\n".join([
            f"- [{item['name']}]({item['url']}) - {item['description']} (⭐ {item['stars']})"
            for item in news_data['github_trending']
        ])

        # Build toutiao hot topics (for generating comments)
        toutiao_hot_section = "\n".join([
            f"- {item['title']}"
            for item in news_data.get('toutiao_hot', [])
        ])

        # Build toutiao content (without links, no numbering) - use all configured data
        tech_headlines = "\n".join([
            f"- {item['title']}\n  {item['summary']}"
            for item in news_data['tech_news']
        ])

        ai_headlines = "\n".join([
            f"- {item['title']}\n  {item['summary']}"
            for item in news_data['ai_news']
        ])

        github_headlines = "\n".join([
            f"- {item['name']}\n  {item['description']} (⭐ {item['stars']})"
            for item in news_data['github_trending']
        ])

        headlines_section = f"""科技热点
{tech_headlines}

AI热点
{ai_headlines}

GitHub热门
{github_headlines}

Toutiao Hot Topics (for generating comments)
{toutiao_hot_section}"""

        prompt = f"""今日是 {today}。请根据以下信息生成一份详细的中文每日科技简报。

## 每日科技热点
{tech_section}

## 每日AI热点
{ai_section}

## GitHub热门项目
{github_section}

请用详细生动的中文撰写，要求：
1. 必须包含以上所有提供的内容，不要遗漏任何一条
2. 每条新闻/热点需要详细展开，字数在200字左右，包括：
   - 简要介绍事件背景
   - 核心内容和关键信息
   - 对行业或用户的影响
   - 简短点评或展望
3. 突出重点，语言生动有趣
4. 使用markdown格式，用##区分板块
        """
        # 调用AI API生成摘要
        content = self._call_ai_api(prompt)
        
        # 调试：检查生成的内容
        if content:
            print("✅ 摘要生成成功")
            print(f"内容长度: {len(content)} 字符")
        else:
            print("❌ 摘要生成失败！")

        return content

from datetime import datetime


class Config:
    """Configuration management class, supports loading configuration from environment variables and GitHub Secrets"""

    def __init__(self):
        # API 配置
        self.api_key = os.getenv('API_KEY') or os.getenv('GLM_API_KEY')
        self.model = os.getenv('MODEL', os.getenv('GLM_MODEL', 'openrouter/free'))
        self.api_base_url = os.getenv('API_BASE_URL') or os.getenv('GLM_BASE_URL', 'https://openrouter.ai/api/v1')
        # Ensure base URL ends without trailing slash for consistent path joining
        self.api_base_url = self.api_base_url.rstrip('/')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '100000'))
        self.timeout = int(os.getenv('TIMEOUT', '60'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))

        # 邮件配置
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO')
        self.email_use_tls = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'

        # 根据邮箱后缀自动配置 SMTP
        smtp_config = self._detect_smtp_config(self.email_from)
        self.email_server = smtp_config['server']
        self.email_port = smtp_config['port']

        # 验证必需的配置项
        required_fields = {
            'API_KEY': self.api_key,
            'EMAIL_FROM': self.email_from,
            'EMAIL_PASSWORD': self.email_password,
            'EMAIL_TO': self.email_to,
        }

        # 新闻配置
        self.max_tech_news = int(os.getenv('MAX_TECH_NEWS', '10'))
        self.max_ai_news = int(os.getenv('MAX_AI_NEWS', '10'))
        self.max_github_repos = int(os.getenv('MAX_GITHUB_REPOS', '10'))

        # 验证必需配置
        self._validate_config()

    def _validate_config(self):
        """验证必需的配置项"""
        required_fields = {
            'API_KEY': self.api_key,
            'EMAIL_FROM': self.email_from,
            'EMAIL_PASSWORD': self.email_password,
            'EMAIL_TO': self.email_to,
        }

        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing_fields)}")

        # 确保 email_port 是整数
        self.email_port = int(self.email_port)

    def get_api_headers(self) -> Dict:
        """Get API request headers (compatible with GLM and other models)"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _detect_smtp_config(self, email: str) -> dict:
        """根据邮箱后缀自动检测 SMTP 配置"""
        if not email:
            return {'server': 'smtp.gmail.com', 'port': 587}

        email = email.lower().strip()
        SMTP_CONFIGS = {
            'qq.com': {'server': 'smtp.qq.com', 'port': 465},
            '163.com': {'server': 'smtp.163.com', 'port': 465},
            '126.com': {'server': 'smtp.126.com', 'port': 465},
            'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
            'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'hotmail.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'yahoo.com': {'server': 'smtp.mail.yahoo.com', 'port': 587},
        }

        for domain, config in SMTP_CONFIGS.items():
            if email.endswith(f'@{domain}'):
                return config

        # 默认返回 Gmail 配置
        return {'server': 'smtp.gmail.com', 'port': 587}

    def to_dict(self) -> Dict:
        """Return configuration dictionary (excluding sensitive information)"""
        return {
            'model': self.model,
            'api_base_url': self.api_base_url,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'email_server': self.email_server,
            'email_port': self.email_port,
            'email_use_tls': self.email_use_tls,
            'max_tech_news': self.max_tech_news,
            'max_ai_news': self.max_ai_news,
            'max_github_repos': self.max_github_repos,
        }


# 全局配置实例
config = Config()