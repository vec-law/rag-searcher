from urllib.parse import urlparse
from bs4 import BeautifulSoup


def parse_links(base_url, content):
    soup = BeautifulSoup(content, "html.parser")
    parsed_base = urlparse(base_url)
    base = f"{parsed_base.scheme}://{parsed_base.netloc}"
    link_dict = {}
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_href = href if href.startswith("http") else f"{base}{href}"
        parsed = urlparse(full_href)
        clean_href = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        link_dict[clean_href] = link.get_text(strip=True)
    return link_dict
