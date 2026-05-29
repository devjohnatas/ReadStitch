from .asura_scraper import AsuraScraper
from .utoon_scraper import UtoonScraper
from .qi_scraper import QiScraper
from .vortex_scraper import VortexScraper
from .comix_scraper import ComixScraper

def get_scraper_for_url(url):
    url_lower = url.lower()
    if 'utoon.net' in url_lower:
        return UtoonScraper()
    elif 'qimanhwa.com' in url_lower:
        return QiScraper()
    elif 'vortexscans.org' in url_lower:
        return VortexScraper()
    elif 'comix.to' in url_lower or 'comick' in url_lower:
        return ComixScraper()
    # Default to Asura
    return AsuraScraper()
