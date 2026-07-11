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
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:300],
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', url)
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return articles[:limit]


def fetch_github_trending(language: str = None, limit: int = 5) -> List[Dict]:
    """获取 GitHub 热门项目"""
    url = GITHUB_TRENDING_URL
    if language:
        url += f"?language={language}"

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        projects = []
        repo_elements = soup.find_all('article', class_='Box-row')[:limit]

        for repo in repo_elements:
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
        return projects
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []


def fetch_crawl_news(source_name: str, limit: int = 5) -> List[Dict]:
    """爬取网站新闻（量子位、机器之心等）"""
    config = CRAWL_SOURCES.get(source_name)
    if not config:
        return []

    try:
        response = requests.get(config['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = []
        items = soup.select(config['list_selector'])[:limit]

        for item in items:
            title_elem = item.select_one(config['title_selector'])
            link_elem = item.select_one(config['link_selector'])
            desc_elem = item.select_one(config['desc_selector'])

            if title_elem:
                articles.append({
                    'title': title_elem.get_text(strip=True),
                    'link': link_elem['href'] if link_elem else config['url'],
                    'summary': desc_elem.get_text(strip=True)[:300] if desc_elem else '',
                    'published': '',
                    'source': source_name
                })
        return articles
    except Exception as e:
        print(f"Error crawling {source_name}: {e}")
        return []


def fetch_all_news() -> Dict:
    """获取所有数据源"""
    # 导入配置
    from generator import config

    # RSS 新闻
    tech_news = fetch_rss_news(RSS_FEEDS['tech'], limit=config.max_tech_news)
    ai_news = fetch_rss_news(RSS_FEEDS['ai'], limit=config.max_ai_news)

    # 如果RSS获取的数量不足，使用爬虫补充
    if config.max_ai_news > 0 and len(ai_news) < config.max_ai_news:
        # 计算需要补充的数量
        needed = config.max_ai_news - len(ai_news)

        # 从量子位获取
        quantum_bit = fetch_crawl_news('quantum_bit', limit=needed)
        ai_news.extend(quantum_bit[:needed])

        # 如果还需要更多，从机器之心获取
        remaining = config.max_ai_news - len(ai_news)
        if remaining > 0:
            machine_heart = fetch_crawl_news('machine_heart', limit=remaining)
            ai_news.extend(machine_heart[:remaining])

    # 确保不超过配置的最大数量
    tech_news = tech_news[:config.max_tech_news]
    ai_news = ai_news[:config.max_ai_news]
    github_trending = fetch_github_trending(limit=config.max_github_repos)

    return {
        'tech_news': tech_news,
        'ai_news': ai_news,
        'github_trending': github_trending
    }