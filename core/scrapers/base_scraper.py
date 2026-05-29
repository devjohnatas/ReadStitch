import os
import urllib.request
import concurrent.futures

class BaseScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def get_chapter_groups(self, series_url):
        # By default, returns a single "Padrão" (Default) group with all chapters
        return {"Padrão": self.get_chapters(series_url)}

    def get_chapters(self, series_url):
        raise NotImplementedError()

    def get_chapter_images(self, chapter_url):
        raise NotImplementedError()

    def download_image(self, url, output_path):
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

    def download_chapter(self, chapter_url, output_dir, chapter_name, max_workers=5):
        target_dir = os.path.join(output_dir, chapter_name)
        os.makedirs(target_dir, exist_ok=True)
        
        images = self.get_chapter_images(chapter_url)
        if not images:
            return 0
            
        def _download(args):
            idx, url = args
            ext = url.split('.')[-1]
            if len(ext) > 4 or '?' in ext: ext = 'jpg'
            filename = f"{idx+1:03d}.{ext}"
            filepath = os.path.join(target_dir, filename)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return filepath
                
            self.download_image(url, filepath)
            return filepath
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(_download, enumerate(images)))
            
        return len(images)
