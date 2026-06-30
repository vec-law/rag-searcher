from curl_cffi import requests


def fetch_url(url: str, fetcher_name: str) -> tuple[str, int]:
    if fetcher_name == "curl":
        return _fetch_curl(url)

    raise ValueError(f"Nieznany fetcher: {fetcher_name}")

def _fetch_curl(url: str) -> tuple[str, int]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    response = requests.get(url, impersonate="chrome", headers=headers)
    return response.text, response.status_code
