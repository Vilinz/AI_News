import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class GLMContentGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        if not self.api_key:
            raise ValueError("GLM_API_KEY is required")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

    def generate_summary(self, news_data: Dict) -> str:
        """使用 GLM 生成每日摘要"""
        today = str(datetime.now().date())

        # 构建输入内容
        tech_section = "\n".join([
            f"- {item['title']} ({item['source']})\n  {item['summary']}"
            for item in news_data['tech_news']
        ])

        ai_section = "\n".join([
            f"- {item['title']} ({item['source']})\n  {item['summary']}"
            for item in news_data['ai_news']
        ])

        github_section = "\n".join([
            f"- [{item['name']}]({item['url']}) - {item['description']} (⭐ {item['stars']})"
            for item in news_data['github_trending']
        ])

        prompt = f"""今日是 {today}。请根据以下信息生成一份中文的每日科技简报。

## 每日科技热点
{tech_section}

## 每日AI热点
{ai_section}

## GitHub热门项目
{github_section}

请用简洁明了的中文撰写，突出重点，每个板块保留3-5条最精彩的内容，并给出简短的点评。"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"生成摘要失败: {str(e)}"

from datetime import datetime