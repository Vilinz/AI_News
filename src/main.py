#!/usr/bin/env python3
"""
每日科技/AI 热点推送服务主入口
"""
import os
from datetime import datetime

from fetchers import fetch_all_news
from generator import GLMContentGenerator
from sender import EmailSender


def main():
    print(f"Starting daily news fetch for {datetime.now().date()}")

    # 1. 获取数据
    print("Fetching news data...")
    news_data = fetch_all_news()
    print(f"Found {len(news_data['tech_news'])} tech news, {len(news_data['ai_news'])} AI news, {len(news_data['github_trending'])} GitHub projects")

    # 2. 生成摘要
    print("Generating summary with GLM...")
    generator = GLMContentGenerator()
    summary = generator.generate_summary(news_data)
    print("Summary generated successfully")

    # 3. 发送邮件
    print("Sending email...")
    sender = EmailSender()
    success = sender.send_news(summary, str(datetime.now().date()))

    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email")
        exit(1)


if __name__ == '__main__':
    main()