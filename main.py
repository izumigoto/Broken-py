import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Broken link: {url} ({response.status})")
                return None
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Failed to crawl {url}: {e}")
        return None

def is_absolute(url):
    return bool(urlparse(url).netloc)

async def crawl(base_url, visited, session):
    html = await fetch(session, base_url)
    if html is None:
        return

    visited.add(base_url)
    soup = BeautifulSoup(html, 'html.parser')
    tasks = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not is_absolute(href):
            href = urljoin(base_url, href)
        if href not in visited:
            visited.add(href)
            tasks.add(crawl(href, visited, session))

    await asyncio.gather(*tasks)

async def main(base_url):
    visited = set()
    async with aiohttp.ClientSession() as session:
        await crawl(base_url, visited, session)
    print("Crawling finished")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <website_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    asyncio.run(main(base_url))
