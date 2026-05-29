import urllib.parse
import urllib.request
import re
import json
import time
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ComixScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "Comix.to"
        
    def _fetch_rendered_with_playwright(self, url: str) -> tuple[str, dict]:
        # Retorna (html, groups_dict)
        from playwright.sync_api import sync_playwright
        from playwright_stealth import Stealth
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/131.0.0.0"
            )
            page = context.new_page()
            Stealth().apply_stealth_sync(page)
            
            # Truque inspirado no Tachiyomi: forçar a API a retornar 100 capítulos de vez
            # ao invés de 20, para acelerar drasticamente a paginação!
            def handle_route(route):
                url = route.request.url
                if '/chapters' in url and 'limit=' in url:
                    import re
                    url = re.sub(r'limit=\d+', 'limit=100', url)
                    route.continue_(url=url)
                else:
                    route.continue_()
            page.route("**/*", handle_route)
            
            page.goto(url, wait_until="domcontentloaded")
            
            # Anti-Cloudflare simple bypass
            for i in range(10):
                title = page.title()
                if not ("Just a moment" in title or "Cloudflare" in title or "Attention Required" in title):
                    break
                page.mouse.move(150 + i*10, 150 + i*10)
                time.sleep(2)
            # Esperar capítulos
            try:
                page.wait_for_selector('.mchap-item, .mchap-row, .chapter-list, a[href*="chapter-"]', timeout=20000)
            except Exception:
                pass
            # Scroll dinâmico para carregar TODOS os capítulos
            previous_height = page.evaluate("document.body.scrollHeight")
            for _ in range(40):
                page.evaluate("window.scrollBy(0, 2000)")
                time.sleep(1.5)
                current_height = page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    # Tentar mais uma vez com scroll para cima e para baixo para forçar
                    page.evaluate("window.scrollBy(0, -500)")
                    time.sleep(0.5)
                    page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(1)
                    current_height = page.evaluate("document.body.scrollHeight")
                    if current_height == previous_height:
                        break # Realmente chegou no fim
                previous_height = current_height
                
            html = page.content()
            
            # Extrair JSON de grupos
            groups_data = []
            try:
                groups_data = page.evaluate('''() => {
                    const s = Array.from(document.querySelectorAll('script')).find(s => s.textContent && s.textContent.includes('groups'));
                    if (s) {
                        try {
                            const data = JSON.parse(s.textContent);
                            const key = Object.keys(data.queries).find(k => k.includes('"groups"'));
                            if (key) return data.queries[key];
                        } catch(e){}
                    }
                    return [];
                }''')
            except Exception:
                pass
                
                
            # Loop pelas páginas de paginação
            groups_dict = {}
            page_count = 1
            
            while True:
                print(f"Lendo página {page_count} dos capítulos...")
                html = page.content()
                
                # Extrair JSON de grupos e capítulos usando BS4
                soup = BeautifulSoup(html, 'html.parser')
                
                # mchap-item pode ser li ou div
                items = soup.find_all(class_=re.compile('mchap-item|mchap-row'))
                
                if items:
                    for item in items:
                        link_tag = item.find('a', class_=re.compile('primary|chapter'))
                        # Fallback if no primary class but has chapter link
                        if not link_tag:
                            links = item.find_all('a', href=re.compile('chapter-'))
                            if links: link_tag = links[0]
                            
                        if link_tag and link_tag.get('href') and 'chapter-' in link_tag.get('href'):
                            href = link_tag['href']
                            full_link = f"https://comix.to{href}" if href.startswith('/') else href
                            
                            group_tag = item.find('a', class_=re.compile('group'))
                            group_name = group_tag.get_text(strip=True) if group_tag else "Padrão"
                            
                            if group_name not in groups_dict:
                                groups_dict[group_name] = []
                            if full_link not in groups_dict[group_name]:
                                groups_dict[group_name].append(full_link)
                
                # Procurar botão de próxima página
                try:
                    next_btn = page.query_selector('button[aria-label="Next page"]')
                    if not next_btn or next_btn.is_disabled():
                        break
                    
                    next_btn.click(force=True)
                    time.sleep(2) # Esperar o React renderizar a nova página
                    page_count += 1
                except Exception as e:
                    print("Erro ao tentar ir para a próxima página:", e)
                    break
            
            if not groups_dict:
                # Fallback genérico apenas na primeira página se não encontrou nada estruturado
                for a in soup.find_all('a'):
                    href = a.get('href', '')
                    if 'chapter-' in href:
                        full_link = f"https://comix.to{href}" if href.startswith('/') else href
                        if "Padrão" not in groups_dict:
                            groups_dict["Padrão"] = []
                        if full_link not in groups_dict["Padrão"]:
                            groups_dict["Padrão"].append(full_link)
                            
            browser.close()
            return html, groups_dict

    def get_chapter_groups(self, series_url: str) -> dict[str, list[str]]:
        html, groups_dict = self._fetch_rendered_with_playwright(series_url)
        
        # Limpar dicionário de grupos vazios
        groups_dict = {k: list(set(v)) for k, v in groups_dict.items() if v}
        
        if not groups_dict:
            raise Exception("Playwright não encontrou capítulos. O Cloudflare pode ter bloqueado ou a página não carregou.")
            
        return groups_dict

    def get_chapters(self, series_url: str) -> list[str]:
        groups = self.get_chapter_groups(series_url)
        all_chaps = []
        for chaps in groups.values():
            all_chaps.extend(chaps)
        return all_chaps

    def get_chapter_images(self, chapter_url: str) -> list[str]:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import Stealth
        import time
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            Stealth().apply_stealth_sync(page)
            
            # Interceptar a API JSON que retorna todas as imagens instantaneamente
            api_images = []
            def handle_response(response):
                if '/api/v1/chapters/' in response.url:
                    try:
                        data = response.json()
                        pages_data = data.get('result', {}).get('pages', {})
                        if not pages_data:
                            pages_data = data.get('chapter', {}).get('images', [])
                            
                        if isinstance(pages_data, dict):
                            base_url = pages_data.get('baseUrl', '').rstrip('/')
                            for item in pages_data.get('items', []):
                                u = item.get('url', '')
                                if u:
                                    api_images.append(u if u.startswith('http') else f"{base_url}/{u.lstrip('/')}")
                        elif isinstance(pages_data, list):
                            for item in pages_data:
                                u = item.get('url', '')
                                if u:
                                    api_images.append(u)
                    except Exception:
                        pass
            page.on('response', handle_response)
            
            page.goto(chapter_url, wait_until="domcontentloaded")
            
            # Tentar extrair do HTML imediatamente (estratégia idêntica ao Tachiyomi)
            try:
                html = page.content()
                import re, json
                
                # Procura por JSON.parse("...") ou JSON.parse('...') contendo os dados do capítulo
                # Muitas vezes os sites Next.js/Nuxt.js injetam o estado assim
                match = re.search(r'JSON\.parse\((["\'].*?["\'])\)', html)
                if match:
                    # Avaliar a string JS para obter o JSON real
                    json_str = page.evaluate(f"() => {match.group(1)}")
                    data = json.loads(json_str)
                    
                    pages_data = data.get('result', {}).get('pages', {})
                    if not pages_data:
                        # Tentar formato alternativo
                        pages_data = data.get('chapter', {}).get('images', [])
                        
                    if isinstance(pages_data, dict):
                        base_url = pages_data.get('baseUrl', '').rstrip('/')
                        for item in pages_data.get('items', []):
                            u = item.get('url', '')
                            if u:
                                api_images.append(u if u.startswith('http') else f"{base_url}/{u.lstrip('/')}")
                    elif isinstance(pages_data, list):
                        for item in pages_data:
                            u = item.get('url', '')
                            if u:
                                api_images.append(u)
                                
                if api_images:
                    browser.close()
                    return api_images
            except Exception as e:
                print("Erro ao tentar extrair JSON embutido:", e)
                
            # Anti-Cloudflare
            for i in range(10):
                title = page.title()
                if not ("Just a moment" in title or "Cloudflare" in title or "Attention Required" in title):
                    break
                page.mouse.move(150 + i*10, 150 + i*10)
                time.sleep(2)
                
            time.sleep(3)
            
            if api_images:
                browser.close()
                return api_images
                
            # FALLBACK: O Comix carrega as imagens via scroll (lazy load)
            print("Interceptação JSON falhou. Usando scroll manual...")
            for _ in range(150):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(0.3)
                is_bottom = page.evaluate("window.scrollY + window.innerHeight >= document.body.scrollHeight")
                if is_bottom:
                    # Tentar esperar para ver se mais imagens carregam no final
                    time.sleep(1)
                    is_bottom_after = page.evaluate("window.scrollY + window.innerHeight >= document.body.scrollHeight")
                    if is_bottom_after:
                        break
                        
            time.sleep(1)
            
            # Coletar as imagens renderizadas
            try:
                images = page.evaluate('''() => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.map(img => img.src || img.getAttribute('data-src')).filter(src => {
                        if (!src) return false;
                        const low = src.toLowerCase();
                        return low.includes('.jpg') || low.includes('.png') || low.includes('.jpeg') || low.includes('.webp');
                    });
                }''')
            except Exception:
                images = []
                
            browser.close()
            
            if not images and not api_images:
                raise Exception("Playwright não encontrou as imagens. O capítulo pode usar canvas ofuscado ou não carregou.")
                
            # Filtrar duplicatas mantendo a ordem
            seen = set()
            ordered = []
            for img in images:
                if img not in seen:
                    seen.add(img)
                    ordered.append(img)
                    
            return ordered
