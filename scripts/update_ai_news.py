#!/usr/bin/env python3
"""
AI新闻自动更新脚本
用于GitHub Actions定时抓取AI技术动态
"""

import json
import os
import re
import ssl
from datetime import datetime
from urllib import request
from urllib.error import URLError

# 禁用SSL验证（某些RSS源可能需要）
ssl._create_default_https_context = ssl._create_unverified_context

# RSS源配置
RSS_SOURCES = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/rss.xml",
    "Google AI": "https://ai.googleblog.com/feeds/posts/default",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
}

# 关键词过滤
KEYWORDS = [
    "GPT", "Claude", "Gemini", "LLM", "大模型", "AI", "模型",
    "LangChain", "LlamaIndex", "RAG", "Agent", "多模态",
    "DeepSeek", "文心一言", "通义千问"
]


def fetch_rss(url, source_name):
    """获取RSS内容"""
    try:
        req = request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(f"获取 {source_name} RSS失败: {e}")
        return None
    except Exception as e:
        print(f"解析 {source_name} 出错: {e}")
        return None


def parse_rss_content(xml_content, source_name):
    """解析RSS XML内容，提取新闻条目"""
    if not xml_content:
        return []
    
    news_items = []
    
    # 简单的正则提取（实际项目中可使用feedparser库）
    item_pattern = r'<item>(.*?)</item>'
    title_pattern = r'<title>(.*?)</title>'
    link_pattern = r'<link>(.*?)</link>'
    desc_pattern = r'<description>(.*?)</description>'
    date_pattern = r'<pubDate>(.*?)</pubDate>'
    
    items = re.findall(item_pattern, xml_content, re.DOTALL)
    
    for item in items[:5]:  # 只取前5条
        title_match = re.search(title_pattern, item)
        link_match = re.search(link_pattern, item)
        desc_match = re.search(desc_pattern, item)
        date_match = re.search(date_pattern, item)
        
        if title_match:
            title = title_match.group(1).strip()
            # 检查是否包含关键词
            if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                news_items.append({
                    "title": title,
                    "link": link_match.group(1).strip() if link_match else "",
                    "description": desc_match.group(1).strip() if desc_match else "",
                    "date": date_match.group(1).strip() if date_match else "",
                    "source": source_name
                })
    
    return news_items


def load_existing_data():
    """加载现有数据"""
    data_file = "data/ai-news.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "lastUpdated": "",
        "version": "1.0",
        "hotNews": [],
        "modelTimeline": [],
        "techTrends": [],
        "toolUpdates": []
    }


def save_data(data):
    """保存数据到JSON文件"""
    os.makedirs("data", exist_ok=True)
    with open("data/ai-news.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_html_from_json():
    """根据JSON数据生成HTML（简化版，实际可扩展）"""
    # 这里可以添加将JSON转换为HTML的逻辑
    # 目前保持HTML静态，只更新JSON数据
    pass


def main():
    """主函数"""
    print(f"开始更新AI新闻数据... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载现有数据
    data = load_existing_data()
    
    # 抓取RSS源
    all_news = []
    for source_name, rss_url in RSS_SOURCES.items():
        print(f"正在获取 {source_name}...")
        xml_content = fetch_rss(rss_url, source_name)
        if xml_content:
            news_items = parse_rss_content(xml_content, source_name)
            all_news.extend(news_items)
            print(f"  找到 {len(news_items)} 条相关新闻")
    
    # 更新数据
    if all_news:
        print(f"\n总共获取 {len(all_news)} 条新闻")
        # 这里可以添加去重、排序等逻辑
        # 将新新闻合并到现有数据中
        
        # 更新最后更新时间
        data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
        
        # 保存数据
        save_data(data)
        print("数据已保存到 data/ai-news.json")
    else:
        print("未获取到新数据")
    
    print("更新完成！")


if __name__ == "__main__":
    main()
