import urllib.request
import urllib.parse
import re
from .base_scraper import BaseScraper

class UtoonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.api_key = "9ab8d5b78e614906ae5a6d869acb833a1a00021819d"

    def _fetch_html(self, url):
        target = urllib.parse.quote(url)
        proxy_url = f'http://api.scrape.do?token={self.api_key}&url={target}&render=true'
        req = urllib.request.Request(proxy_url, headers=self.headers)
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')

    def get_chapters(self, series_url):
        if "chapter-" in series_url or "/chapter" in series_url:
            return [series_url]
            
        try:
            html = self._fetch_html(series_url)
        except Exception as e:
            raise Exception(f"Failed to fetch Utoon series: {e}")

        parts = [p for p in series_url.split('/') if p]
        slug = parts[-1] if parts else ""
        
        pattern = r'href=[\'\"](https://utoon\.net/manga/' + re.escape(slug) + r'/chapter-[^\'\"]+)[\'\"]'
        links = set(re.findall(pattern, html))
        
        def extract_num(path):
            match = re.search(r'chapter-(\d+(?:\.\d+)?)', path)
            return float(match.group(1)) if match else 0
            
        sorted_links = sorted(list(links), key=extract_num)
        return sorted_links

    def get_chapter_images(self, chapter_url):
        try:
            html = self._fetch_html(chapter_url)
        except Exception as e:
            raise Exception(f"Failed to fetch Utoon chapter: {e}")
            
        images = re.findall(r'(https://utoon\.net/wp-content/uploads/WP-manga/data/[^\s\'\"]+)', html)
        
        seen = set()
        ordered = []
        for img in images:
            img = img.strip()
            if img not in seen:
                seen.add(img)
                ordered.append(img)
                
        return ordered
