"""Scrapes property listings from PropertyFinder UAE."""
import time, random, logging, hashlib
from typing import List, Optional, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

logger = logging.getLogger(__name__)

class PropertyFinderScraper:
    """Rate-limited scraper for PropertyFinder.ae with pagination support."""

    BASE_URL = "https://www.propertyfinder.ae"
    SEARCH_PATH = "/en/properties-for-sale.html"
    MAX_RESULTS_PER_PAGE = 40
    RATE_LIMIT_MIN = 2.0
    RATE_LIMIT_MAX = 5.0
    MAX_RETRIES = 3

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, delay_range: tuple = None):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.delay_range = delay_range or (self.RATE_LIMIT_MIN, self.RATE_LIMIT_MAX)
        self._request_count = 0
        self._error_count = 0
        self._last_request_time = 0

    def _respectful_delay(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        delay = random.uniform(*self.delay_range)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """Make a rate-limited HTTP request with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            self._respectful_delay()
            try:
                response = self.session.get(url, params=params, timeout=30)
                self._request_count += 1
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 60))
                    logger.warning("Rate limited, waiting %d seconds", wait)
                    time.sleep(wait)
                else:
                    logger.warning("HTTP %d for %s", response.status_code, url)
            except requests.RequestException as e:
                logger.error("Request failed (attempt %d/%d): %s",
                             attempt + 1, self.MAX_RETRIES, e)
                self._error_count += 1
                time.sleep(2 ** attempt)
        return None

    def search_properties(self, emirate: str = "dubai", property_type: str = None,
                          min_price: int = None, max_price: int = None,
                          min_bedrooms: int = None, page: int = 1) -> List[Dict]:
        """Search for properties with filters."""
        params = {"page": page}
        if property_type:
            params["type"] = property_type
        if min_price:
            params["min_price"] = min_price
        if max_price:
            params["max_price"] = max_price
        if min_bedrooms is not None:
            params["bedrooms"] = min_bedrooms
        url = f"{self.BASE_URL}/en/properties-for-sale/{emirate}/"
        html = self._make_request(url, params)
        if not html:
            return []
        return self._parse_search_results(html)

    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results page into property dictionaries."""
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        cards = soup.find_all("article", class_="property-card")
        if not cards:
            cards = soup.find_all("div", {"data-test": "property-card"})
        for card in cards:
            try:
                listing = self._parse_single_card(card)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.debug("Failed to parse card: %s", e)
        return listings

    def _parse_single_card(self, card) -> Optional[Dict]:
        """Extract property data from a single search result card."""
        title_el = card.find("h2") or card.find("a", class_="property-card-title")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        link = title_el.find("a") or card.find("a")
        url = link["href"] if link and link.get("href") else None
        price_el = card.find("span", class_="property-card-price")
        price_text = price_el.get_text(strip=True) if price_el else ""
        price = self._parse_price(price_text)
        specs = card.find_all("li", class_="property-card-specification")
        bedrooms, bathrooms, sqft = None, None, None
        for spec in specs:
            text = spec.get_text(strip=True).lower()
            if "bed" in text:
                bedrooms = self._extract_number(text)
            elif "bath" in text:
                bathrooms = self._extract_number(text)
            elif "sq" in text or "ft" in text:
                sqft = self._extract_number(text)
        location_el = card.find("span", class_="property-card-location")
        area = location_el.get_text(strip=True) if location_el else ""
        return {
            "title": title, "url": url, "price_aed": price,
            "bedrooms": bedrooms, "bathrooms": bathrooms,
            "size_sqft": sqft, "area": area,
            "source": "propertyfinder", "scraped_at": datetime.utcnow().isoformat(),
        }

    def _parse_price(self, text: str) -> float:
        """Parse price text to numeric AED value."""
        text = text.replace(",", "").replace("AED", "").strip()
        if "k" in text.lower():
            return float(text.lower().replace("k", "").strip()) * 1000
        if "m" in text.lower():
            return float(text.lower().replace("m", "").strip()) * 1000000
        try:
            return float("".join(c for c in text if c.isdigit() or c == "."))
        except ValueError:
            return 0.0

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract first number from text."""
        import re
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def get_listing_detail(self, url: str) -> Optional[Dict]:
        """Fetch and parse a single listing's detail page."""
        html = self._make_request(url)
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        detail = {"url": url, "source": "propertyfinder"}
        title = soup.find("h1")
        if title:
            detail["title"] = title.get_text(strip=True)
        desc = soup.find("div", class_="property-description")
        if desc:
            detail["description"] = desc.get_text(strip=True)[:1000]
        return detail

    @property
    def stats(self) -> Dict:
        return {"requests": self._request_count, "errors": self._error_count}
