import time
import logging
from urllib.parse import urlparse
from collections import Counter
from rag_searcher.core.fetcher import fetch_url
from rag_searcher.core.link_parser import parse_links

logger = logging.getLogger(__name__)


def fetch_links_from_paginated(url, page_max, fetcher_name):
    if not page_max or "{page_number}" not in url:
        return

    url_dict = {}
    first_links = None
    prev_links = None

    for i in range(1, page_max + 1):
        page_url = url.replace("{page_number}", str(i))
        content, status_code = fetch_url(page_url, fetcher_name)
        logger.info("[page: %s, status: %s] %s", i, status_code, page_url[:80])

        if status_code != 200:
            break

        url_dict[page_url] = parse_links(page_url, content)

        if i == 1:
            first_links = set(url_dict[page_url].keys())

        if i >= 3 and prev_links is not None:
            curr_links = set(url_dict[page_url].keys())
            union_prev = len(prev_links | curr_links)
            union_first = len(first_links | curr_links)
            if ((union_prev > 0 and len(prev_links & curr_links) / union_prev >= 0.8) or
                    (union_first > 0 and len(first_links & curr_links) / union_first >= 0.8)):
                break

        time.sleep(2)
        prev_links = set(url_dict[page_url].keys())

    if not url_dict:
        return

    return _filter_links(url_dict)

def _filter_links(url_dict):
    common = set()
    if len(url_dict) >= 2:
        keys = list(url_dict.keys())
        common = set(url_dict[keys[0]].keys())
        for url in keys[1:3]:
            common &= set(url_dict[url].keys())

    link_dict = {}
    for url in url_dict:
        for link in url_dict[url]:
            if link not in common:
                link_dict[link] = url_dict[url][link]

    segments = [parts[1] for link in link_dict if len(parts := urlparse(link).path.split("/")) > 1]
    counter = Counter(segments)
    if not counter:
        return None
    dominant = {max(counter, key=counter.get)}

    return {
        link: link_dict[link]
        for link in link_dict
        if len(parts := urlparse(link).path.split("/")) > 1 and parts[1] in dominant
    }
