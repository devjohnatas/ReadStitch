from .asura_scraper import AsuraScraper
from .utoon_scraper import UtoonScraper
from .qi_scraper import QiScraper
from .vortex_scraper import VortexScraper
from .comix_scraper import ComixScraper
from .webtoon_scraper import WebtoonScraper
from .kakao_scraper import KakaoScraper
from .piccoma_scraper import PiccomaScraper

def get_scraper_for_url(url):
    url_lower = url.lower()
    if 'webtoons.com' in url_lower:
        return WebtoonScraper()
    elif 'kakao.com' in url_lower:
        return KakaoScraper()
    elif 'utoon.net' in url_lower:
        return UtoonScraper()
    elif 'qimanhwa.com' in url_lower:
        return QiScraper()
    elif 'vortexscans.org' in url_lower:
        return VortexScraper()
    elif 'comix.to' in url_lower or 'comick' in url_lower:
        return ComixScraper()
    elif 'piccoma.com' in url_lower:
        return PiccomaScraper()
    # Default to Asura
    return AsuraScraper()
