import os
import urllib.request
import urllib.parse
import json
import re
from .base_scraper import BaseScraper

class QiScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.api_key = "9ab8d5b78e614906ae5a6d869acb833a1a00021819d"
        
    @property
    def name(self) -> str:
        return "Qimanhwa"
        
    def _fetch_via_proxy(self, url: str, render=True) -> str:
        target = urllib.parse.quote(url)
        render_param = "&render=true" if render else ""
        proxy_url = f"http://api.scrape.do?token={self.api_key}&url={target}{render_param}"
        req = urllib.request.Request(proxy_url, headers=self.headers)
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
            
    def get_chapters(self, series_url: str) -> list[str]:
        if "/chapter" in series_url:
            return [series_url]
            
        html = self._fetch_via_proxy(series_url)
        
        slug = [p for p in series_url.split('/') if p][-1]
        pattern = r'href=[\'\"](/series/' + re.escape(slug) + r'/chapter-[0-9]+)[\'\"]'
        links = re.findall(pattern, html)
        
        chapters = set()
        for href in links:
            full_url = f"https://qimanhwa.com{href}" if href.startswith('/') else href
            chapters.add(full_url)
                
        def get_chap_num(url):
            try:
                return float(url.split('chapter-')[-1].split('/')[0].replace('-', '.'))
            except:
                return 0
                
        return sorted(list(chapters), key=get_chap_num, reverse=True)

    def get_chapter_images(self, chapter_url: str) -> list[str]:
        parts = chapter_url.strip('/').split('/series/')
        if len(parts) < 2:
            raise Exception("URL de capítulo inválida")
        
        slug_part = parts[1]
        slugs = slug_part.split('/')
        if len(slugs) < 2:
            raise Exception("Formato de slug inválido")
            
        series_slug = slugs[0]
        chapter_slug = slugs[1]
        
        api_url = f"https://api.qimanhwa.com/api/v1/series/{series_slug}/chapters/{chapter_slug}"
        
        json_str = self._fetch_via_proxy(api_url, render=False)
        data = json.loads(json_str)
        
        if data.get('requiresPurchase', False) and not data.get('images'):
            raise Exception(f"O capítulo {chapter_slug} é pago e está bloqueado.")
            
        images = data.get('images', [])
        if not images:
            raise Exception("Nenhuma imagem encontrada.")
            
        ordered = []
        for img_obj in images:
            img_url = img_obj.get('url')
            if img_url:
                target_encoded = urllib.parse.quote(img_url)
                proxy_url = f"http://api.scrape.do?token={self.api_key}&url={target_encoded}"
                ordered.append(proxy_url)
                
        return ordered
