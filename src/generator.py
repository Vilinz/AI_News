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

    def generate_summary(self, news_data: Dict) -> str:
        """使用 GLM 生成每日摘要"""
        today = str(datetime.now().date())

        # 构建输入内容（包含链接）
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

        # 构建今日头条内容（不带链接）
        tech_headlines = "\n".join([
            f"- {item['title']}\n  {item['summary']}"
            for item in news_data['tech_news'][:3]  # 科技热点精选3条
        ])

        ai_headlines = "\n".join([
            f"- {item['title']}\n  {item['summary']}"
            for item in news_data['ai_news'][:2]  # AI热点精选2条
        ])

        github_headlines = "\n".join([
            f"- {item['name']} - {item['description']} (⭐ {item['stars']})"
            for item in news_data['github_trending'][:2]  # GitHub精选2条
        ])

        headlines_section = f"""**科技热点**
{tech_headlines}

**AI热点**
{ai_headlines}

**GitHub热门**
{github_headlines}"""

        prompt = f"""今日是 {today}。请根据以下信息生成一份中文的每日科技简报。

## 每日科技热点
{tech_section}

## 每日AI热点
{ai_section}

## GitHub热门项目
{github_section}

## 今日头条
{headlines_section}

请用简洁明了的中文撰写，突出重点，每个板块保留3-5条最精彩的内容，并给出简短的点评。
重要：在输出时，每条新闻必须保留原始链接，格式为「标题 | 链接」"""

        # 使用配置参数
        timeout = self.timeout

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=config.get_api_headers(),
                    json={
                        "model": config.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": self.max_tokens
                    },
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()

                # 根据不同的 API 格式处理响应
                if 'choices' in result:
                    # OpenAI/GLM 格式
                    return result['choices'][0]['message']['content']
                elif 'content' in result:
                    # 直接返回内容
                    return result['content']
                elif 'response' in result:
                    # 其他格式
                    return result['response']
                else:
                    return str(result)

            except Timeout as e:
                if attempt < max_retries - 1:
                    # 指数退避：2^attempt * 1秒，最多等待4秒
                    wait_time = min(2 ** attempt, 4)
                    print(f"请求超时，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"达到最大重试次数，请求超时: {e}")
                    return f"生成摘要失败: 请求超时 (已重试{max_retries}次)"

            except RequestException as e:
                # 打印更详细的错误信息
                print(f"请求失败详情:")
                print(f"  - URL: {e.request.url if hasattr(e, 'request') else 'N/A'}")
                print(f"  - 状态码: {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'}")
                if hasattr(e, 'response') and e.response:
                    print(f"  - 响应内容: {e.response.text[:200]}...")
                return f"生成摘要失败: {str(e)}"

            except Exception as e:
                print(f"未知错误: {e}")
                return f"生成摘要失败: {str(e)}"

from datetime import datetime


class Config:
    """配置管理类，支持从环境变量和 GitHub Secrets 加载配置"""

    def __init__(self):
        # API 配置
        self.api_key = os.getenv('API_KEY') or os.getenv('GLM_API_KEY')
        self.model = os.getenv('MODEL', os.getenv('GLM_MODEL', 'glm-4-flash'))
        self.api_base_url = os.getenv('API_BASE_URL') or os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        self.timeout = int(os.getenv('TIMEOUT', '60'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))

        # 邮件配置
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO')
        self.email_server = os.getenv('EMAIL_SERVER', 'smtp.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', '587'))
        self.email_use_tls = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'

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

    def get_api_headers(self) -> Dict:
        """获取 API 请求头（兼容 GLM 和其他模型）"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def to_dict(self) -> Dict:
        """返回配置字典（不包含敏感信息）"""
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