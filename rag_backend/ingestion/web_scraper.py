# currently just extracts text from a webpage. we can extend this to include more 
# features like images, links, etc.

import trafilatura
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class PageScraper:
    def __init__(self, include_comments=False, include_tables=False):
        self.include_comments = include_comments
        self.include_tables = include_tables

    def scrape_clean_text(self, url: str) -> str | None:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(
                downloaded,
                include_comments=self.include_comments,
                include_tables=self.include_tables
            )
        return None


class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 5, scraper: PageScraper = None):
        self.base_url = base_url
        self.max_pages = max_pages
        self.scraper = scraper if scraper else PageScraper()
        self.visited = set()
        self.to_visit = [base_url]
        self.contents = []

    def crawl(self):
        while self.to_visit and len(self.visited) < self.max_pages:
            current_url = self.to_visit.pop(0)
            if current_url in self.visited:
                continue

            try:
                response = requests.get(current_url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                text = self.scraper.scrape_clean_text(current_url)
                if text:
                    self.contents.append({
                        "url": current_url,
                        "text": text
                    })

                self.visited.add(current_url)
                self._queue_internal_links(soup)

            except Exception as e:
                print(f"⚠️ Skipped {current_url}: {e}")

        return self.contents

    def _queue_internal_links(self, soup: BeautifulSoup):
        for a in soup.find_all("a", href=True):
            next_url = urljoin(self.base_url, a["href"])
            if self.base_url in next_url and next_url not in self.visited and next_url not in self.to_visit:
                self.to_visit.append(next_url)

# Example usage
if __name__ == "__main__":
    print("Starting web scraping...")
    base_url = "https://docs.utilihive.io/utilihive-integration/"
    scraper = PageScraper()
    crawler = WebsiteCrawler(base_url, max_pages=10, scraper=scraper)

    results = crawler.crawl()

    print(f"✅ Scraped {len(results)} pages.")
    if results:
        print(results[0]['text'][:1000])
