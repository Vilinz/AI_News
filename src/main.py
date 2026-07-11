#!/usr/bin/env python3
"""
每日科技/AI 热点推送服务主入口
"""
import os
import json
from datetime import datetime

from fetchers import fetch_all_news
from generator import GLMContentGenerator, config
from sender import EmailSender


def main():
    start_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"🚀 启动每日科技简报生成 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # 打印配置信息（不包含敏感信息）
    print("📋 当前配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    print()

    # 1. 获取数据
    print("📰 第一步：获取新闻数据...")
    print("-" * 40)
    news_data = fetch_all_news()
    print("-" * 40)
    print(f"✅ 数据获取完成：")
    print(f"   - 科技新闻：{len(news_data['tech_news'])} 条")
    print(f"   - AI新闻：{len(news_data['ai_news'])} 条")
    print(f"   - GitHub项目：{len(news_data['github_trending'])} 个\n")

    # 2. 生成摘要
    print("🤖 第二步：生成AI摘要...")
    print("-" * 40)
    print(f"正在使用 {config.model} 模型生成摘要...")
    generator = GLMContentGenerator()
    summary = generator.generate_summary(news_data)
    print("-" * 40)
    print("✅ 摘要生成完成！")
    print(f"摘要长度：{len(summary)} 字符\n")

    # 3. 发送邮件
    print("📧 第三步：发送邮件...")
    print("-" * 40)
    sender = EmailSender()
    success = sender.send_news(summary, str(datetime.now().date()))
    print("-" * 40)

    if success:
        print("✅ 邮件发送成功！")
        print(f"\n🎉 任务完成！耗时：{(datetime.now() - start_time).total_seconds():.2f} 秒")
        print("="*60)
    else:
        print("❌ 邮件发送失败！")
        exit(1)


if __name__ == '__main__':
    main()