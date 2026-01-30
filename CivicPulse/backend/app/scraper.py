"""Data scraping module for RSS feeds, Reddit, and HTML sources."""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import re


def scrape_rss_feeds(feed_urls: List[str]) -> List[Dict[str, Any]]:
    """Scrape RSS feeds and return list of articles."""
    articles = []
    
    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    published = datetime.utcnow()
                
                # Combine title and summary for text
                text = ""
                if hasattr(entry, 'title'):
                    text += entry.title + " "
                if hasattr(entry, 'summary'):
                    text += entry.summary
                if hasattr(entry, 'description'):
                    text += " " + entry.description
                
                articles.append({
                    "source": f"rss:{feed_url}",
                    "title": getattr(entry, 'title', 'No title'),
                    "text": text.strip(),
                    "published": published,
                    "url": getattr(entry, 'link', '')
                })
        except Exception as e:
            print(f"Error scraping RSS feed {feed_url}: {e}")
            continue
    
    return articles


def scrape_reddit_rss(subreddit: str) -> List[Dict[str, Any]]:
    """Scrape Reddit subreddit via RSS feed."""
    rss_url = f"https://www.reddit.com/r/{subreddit}/.rss"
    return scrape_rss_feeds([rss_url])


def scrape_police_blotter(url: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
    """Scrape HTML police blotter page for safety-related content."""
    if keywords is None:
        keywords = [
            "arrest", "robbery", "assault", "theft", "burglary",
            "accident", "crash", "collision", "fire", "emergency",
            "incident", "crime", "violence", "shooting", "stabbing"
        ]
    
    articles = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all paragraphs and divs
        text_elements = soup.find_all(['p', 'div', 'article', 'section'])
        
        for element in text_elements:
            text = element.get_text(strip=True)
            if not text or len(text) < 50:  # Skip very short text
                continue
            
            # Check if text contains any keywords
            text_lower = text.lower()
            if any(keyword.lower() in text_lower for keyword in keywords):
                # Try to extract title from parent or heading
                title = "Police Blotter Entry"
                heading = element.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if heading:
                    title = heading.get_text(strip=True)
                
                # Try to extract date from text
                published = datetime.utcnow()
                date_patterns = [
                    r'\d{1,2}/\d{1,2}/\d{4}',
                    r'\d{4}-\d{2}-\d{2}',
                    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}'
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            # Simple date parsing (can be improved)
                            date_str = match.group(0)
                            if '/' in date_str:
                                parts = date_str.split('/')
                                if len(parts) == 3:
                                    published = datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                            break
                        except:
                            pass
                
                articles.append({
                    "source": f"html:{url}",
                    "title": title,
                    "text": text,
                    "published": published,
                    "url": url
                })
    except Exception as e:
        print(f"Error scraping police blotter {url}: {e}")
    
    return articles


def run_one_shot() -> List[Dict[str, Any]]:
    """Run a one-shot scrape of all configured sources."""
    all_articles = []
    
    # Sample RSS feeds (can be configured via env)
    rss_feeds = [
        "https://www.nyc.gov/rss/feeds/cityhall.rss",
        "https://www1.nyc.gov/nyc-resources/feeds/all.rss",
        # Add more city-specific feeds
    ]
    
    # Scrape RSS feeds
    print("Scraping RSS feeds...")
    rss_articles = scrape_rss_feeds(rss_feeds)
    all_articles.extend(rss_articles)
    print(f"Found {len(rss_articles)} RSS articles")
    
    # Scrape Reddit (example: NYC subreddit)
    print("Scraping Reddit...")
    try:
        reddit_articles = scrape_reddit_rss("nyc")
        all_articles.extend(reddit_articles)
        print(f"Found {len(reddit_articles)} Reddit posts")
    except Exception as e:
        print(f"Reddit scraping failed: {e}")
    
    # Scrape sample police blotter (example URL - user should configure)
    police_blotter_urls = [
        # Add actual police blotter URLs here
        # "https://example.com/police-blotter"
    ]
    
    for url in police_blotter_urls:
        print(f"Scraping police blotter: {url}")
        try:
            blotter_articles = scrape_police_blotter(url)
            all_articles.extend(blotter_articles)
            print(f"Found {len(blotter_articles)} blotter entries")
        except Exception as e:
            print(f"Police blotter scraping failed: {e}")
    
    print(f"Total articles scraped: {len(all_articles)}")
    return all_articles
