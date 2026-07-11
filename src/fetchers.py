import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict

# 数据源配置
RSS_FEEDS = {
    'tech': [
        # 国外
        'https://www.theverge.com/rss/index.xml',
        'https://techcrunch.com/feed/',
        # 国内
        'https://36kr.com/feed',
        'https://www.huxiu.com/rss/0.xml',
        'https://www.infoq.cn/feed',
        'https://www.v2ex.com/index.xml',
    ],
    'ai': [
        # 国外
        'https://www.artificialintelligence-news.com/feed/',
        'https://openai.com/blog/rss.xml',
        # 国内（通过爬虫获取）
    ]
}

# 需要爬取的网站配置
CRAWL_SOURCES = {
    'quantum_bit': {
        'url': 'https://www.qbitai.com',
        'list_selector': '.article-item',
        'title_selector': 'h2',
        'link_selector': 'a',
        'desc_selector': '.excerpt',
    },
    'machine_heart': {
        'url': 'https://www.jiqizhixin.com',
        'list_selector': '.article-item',
        'title_selector': 'h3',
        'link_selector': 'a',
        'desc_selector': '.summary',
    }
}

GITHUB_TRENDING_URL = "https://github.com/trending"


def fetch_rss_news(feed_urls: List[str], limit: int = 5) -> List[Dict]:
    """从 RSS feeds 获取新闻"""
    articles = []
    print(f"开始从 {len(feed_urls)} 个 RSS 源获取新闻，限制 {limit} 条")

    for url in feed_urls:
        print(f"正在处理 RSS 源: {url}")
        try:
            feed = feedparser.parse(url)
            feed_title = feed.feed.get('title', url)
            print(f"成功获取 RSS 源: {feed_title}, 包含 {len(feed.entries)} 条新闻")

            entry_count = 0
            for entry in feed.entries[:limit]:
                entry_count += 1
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:300],
                    'published': entry.get('published', ''),
                    'source': feed_title
                })

            print(f"从 {feed_title} 提取了 {entry_count} 条新闻")

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    print(f"RSS 新闻获取完成，共 {len(articles)} 条")
    return articles[:limit]


def fetch_github_trending(language: str = None, limit: int = 5) -> List[Dict]:
    """获取 GitHub 热门项目"""
    url = GITHUB_TRENDING_URL
    if language:
        url += f"?language={language}"

    print(f"正在获取 GitHub 热门项目，语言: {language or '全部'}, 限制: {limit} 条")
    print(f"请求 URL: {url}")

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        projects = []
        repo_elements = soup.find_all('article', class_='Box-row')
        print(f"页面找到 {len(repo_elements)} 个项目元素")

        for i, repo in enumerate(repo_elements[:limit]):
            repo_title = repo.find('h2')
            if repo_title:
                repo_link = repo_title.find('a')
                if repo_link:
                    repo_name = repo_link.text.strip().replace('\n', '').replace(' ', '')
                    repo_url = 'https://github.com' + repo_link['href']

                    # 获取描述
                    desc = repo.find('p')
                    description = desc.text.strip() if desc else 'No description'

                    # 获取星标数
                    stars = repo.find('span', class_='d-inline-block float-sm-right')
                    star_count = stars.text.strip() if stars else '0'

                    projects.append({
                        'name': repo_name,
                        'url': repo_url,
                        'description': description[:200],
                        'stars': star_count
                    })
                    print(f"  {i+1}. {repo_name} - {star_count} stars")

        print(f"GitHub 热门项目获取完成，共 {len(projects)} 条")
        return projects
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []


def fetch_crawl_news(source_name: str, limit: int = 5) -> List[Dict]:
    """爬取网站新闻（量子位、机器之心等）"""
    config = CRAWL_SOURCES.get(source_name)
    if not config:
        print(f"未找到爬虫配置: {source_name}")
        return []

    print(f"开始爬取 {source_name} 新闻，限制 {limit} 条")
    print(f"请求 URL: {config['url']}")

    try:
        response = requests.get(config['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = []
        items = soup.select(config['list_selector'])
        print(f"页面找到 {len(items)} 个项目元素")

        for i, item in enumerate(items[:limit]):
            title_elem = item.select_one(config['title_selector'])
            link_elem = item.select_one(config['link_selector'])
            desc_elem = item.select_one(config['desc_selector'])

            if title_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem['href'] if link_elem else config['url']
                summary = desc_elem.get_text(strip=True)[:300] if desc_elem else ''

                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': '',
                    'source': source_name
                })
                print(f"  {i+1}. {title}")

        print(f"{source_name} 爬取完成，共 {len(articles)} 条")
        return articles
    except Exception as e:
        print(f"Error crawling {source_name}: {e}")
        return []


def fetch_all_news() -> Dict:
    """获取所有数据源"""
    # 导入配置
    from generator import config

    print("\n" + "="*50)
    print("开始获取每日新闻数据")
    print("="*50)
    print(f"配置 - 科技新闻: {config.max_tech_news} 条, AI新闻: {config.max_ai_news} 条, GitHub: {config.max_github_repos} 条")

    # RSS 新闻
    print("\n【科技新闻 RSS】")
    tech_news = fetch_rss_news(RSS_FEEDS['tech'], limit=config.max_tech_news)

    print("\n【AI新闻 RSS】")
    ai_news = fetch_rss_news(RSS_FEEDS['ai'], limit=config.max_ai_news)

    # 如果RSS获取的数量不足，使用爬虫补充
    if config.max_ai_news > 0 and len(ai_news) < config.max_ai_news:
        print(f"\nAI新闻 RSS 获取不足 ({len(ai_news)}/{config.max_ai_news})，开始爬虫补充...")

        # 计算需要补充的数量
        needed = config.max_ai_news - len(ai_news)
        print(f"需要补充 {needed} 条 AI 新闻")

        # 从量子位获取
        print("\n【爬虫 - 量子位】")
        quantum_bit = fetch_crawl_news('quantum_bit', limit=needed)
        ai_news.extend(quantum_bit[:needed])
        print(f"量子位添加了 {min(len(quantum_bit), needed)} 条")

        # 如果还需要更多，从机器之心获取
        remaining = config.max_ai_news - len(ai_news)
        if remaining > 0:
            print(f"\n仍需补充 {remaining} 条 AI 新闻")
            print("\n【爬虫 - 机器之心】")
            machine_heart = fetch_crawl_news('machine_heart', limit=remaining)
            ai_news.extend(machine_heart[:remaining])
            print(f"机器之心添加了 {min(len(machine_heart), remaining)} 条")

    # 确保不超过配置的最大数量
    tech_news = tech_news[:config.max_tech_news]
    ai_news = ai_news[:config.max_ai_news]

    print("\n【GitHub 热门项目】")
    github_trending = fetch_github_trending(limit=config.max_github_repos)

    # 最终统计
    print("\n" + "="*50)
    print("新闻获取完成！")
    print("="*50)
    print(f"科技新闻: {len(tech_news)} 条")
    print(f"AI新闻: {len(ai_news)} 条")
    print(f"GitHub项目: {len(github_trending)} 条")
    print("="*50 + "\n")

    return {
        'tech_news': tech_news,
        'ai_news': ai_news,
        'github_trending': github_trending
    }