import trafilatura


def extract_content(html: str) -> str | None:
    return trafilatura.extract(
        html,
        include_tables=True,
        include_links=False,
        favor_recall=True,
        include_formatting=True,
        include_images=False,
    )
