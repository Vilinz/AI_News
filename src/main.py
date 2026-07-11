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
    print(f"   - GitHub项目：{len(news_data['github_trending'])} 个")
    print(f"   - 今日头条热点：{len(news_data.get('toutiao_hot', []))} 条\n")

    # 2. 生成摘要
    print("🤖 第二步：生成AI摘要...")
    print("-" * 40)
    print(f"正在使用 {config.model} 模型生成摘要...")
    print("开始调用 AI API...")
    generator = GLMContentGenerator()
    print("正在生成摘要，这可能需要几秒钟...")
    summary = generator.generate_summary(news_data)
    print("-" * 40)
    print("✅ 摘要生成完成！")
    print(f"摘要长度：{len(summary)} 字符\n")

    # 3. 为今日头条热点生成微头条文章
    print("📝 第三步：生成今日头条微头条文章...")
    print("-" * 40)
    toutiao_hot = news_data.get('toutiao_hot', [])
    toutiao_articles = []
    
    # 选取10个热点
    hot_topics = toutiao_hot[:10]
    print(f"选取 {len(hot_topics)} 个热点生成微头条文章\n")
    
    for i, topic in enumerate(hot_topics, 1):
        print(f"[{i}/{len(hot_topics)}] 正在为热点生成微头条...")
        article = generator.generate_toutiao_article(topic['title'])
        toutiao_articles.append({
            'title': topic['title'],
            'content': article
        })
        print(f"  ✅ 完成 - 文章长度: {len(article)} 字符\n")
    
    print("-" * 40)
    print(f"✅ 微头条文章生成完成！共 {len(toutiao_articles)} 篇\n")

    # 4. 组合最终内容
    print("📄 第四步：组合最终内容...")
    print("-" * 40)
    
    # 构建微头条部分
    toutiao_section = "\n\n" + "="*50 + "\n"
    toutiao_section += "📱 今日头条微头条文章\n"
    toutiao_section += "="*50 + "\n\n"
    
    for i, article in enumerate(toutiao_articles, 1):
        toutiao_section += f"【热点{i}】{article['title']}\n"
        toutiao_section += "-"*30 + "\n"
        toutiao_section += article['content'] + "\n\n"
    
    # 组合完整内容
    full_content = summary + toutiao_section
    
    print(f"✅ 最终内容组合完成！总长度: {len(full_content)} 字符\n")

    # 5. 发送邮件
    print("📧 第五步：发送邮件...")
    print("-" * 40)
    sender = EmailSender()
    success = sender.send_news(full_content, str(datetime.now().date()))
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