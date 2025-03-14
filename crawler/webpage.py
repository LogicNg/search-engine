from collections import deque
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from database.add_pages import add_pages
from database.should_fetch_page import should_fetch_page


def fetch_webpage(url: str) -> Dict[str, Optional[str]]:
    """
    Fetches the content of a webpage using the provided URL.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        Dict[str, Optional[str]]: A dictionary containing:
            - "html" (str): The HTML content of the webpage.
            - "last_modified" (str or None): The value of the "Last-Modified" header if available, otherwise None.
    """
    response = requests.get(url)
    html_content = response.text
    last_modified = response.headers.get("Last-Modified")
    return {
        "html": html_content,
        "last_modified": last_modified,
    }


def parse_webpage(html: str, base_url: str) -> Dict[str, Optional[object]]:
    """
    Parses the webpage HTML to extract the title, body text, and all URLs.

    Args:
        html (str): The HTML content of the webpage.
        base_url (str): The base URL to resolve relative URLs.

    Returns:
        Dict[str, Optional[object]]: A dictionary containing:
            - "title" (str): The title of the webpage, or None if not found.
            - "body_text" (str): The combined text of the body content.
            - "urls" (List[str]): A list of all URLs found in anchor tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else None
    body_text = " ".join(p.get_text() for p in soup.find_all("p"))
    urls = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)]
    Dict = {}
    Dict["title"] = title
    Dict["body_text"] = body_text
    Dict["urls"] = urls
    return Dict


def recursive_fetch(base_url: str) -> List[Dict[str, Optional[str]]]:
    """
    Recursively fetches webpages starting from the specified base URL using a breadth-first search (BFS) strategy while avoiding cyclic links.

    Args:
        base_url (str): The initial URL from which to begin fetching webpages.

    Returns:
        List[Dict[str, Optional[str]]]: A list of dictionaries, each containing:
            - "body_text" (str): The main text content of the fetched webpage.
            - "last_modified" (str or None): The value of the "Last-Modified" header for the fetched webpage, if available; otherwise, None.
            - "parent_url" (str or None): The URL of the webpage that initiated the fetch; can be None for the root URL.
            - "title" (str): The title of the fetched webpage.
            - "url" (str): The URL of the fetched webpage.

    This function will continue to fetch and parse webpages until all reachable URLs are visited, ensuring that:
    - Each URL is fetched only once, preventing infinite loops caused by cyclic links.
    - Successfully handles and tracks previously visited URLs to avoid redundant fetches.
    """
    visited: Set[str] = set()
    queue = deque([(base_url, None)])  # (current_url, parent_url)
    results = []

    while queue:
        current_url, parent_url = queue.popleft()
        if current_url in visited:
            continue

        visited.add(current_url)
        try:
            print(current_url)
            webpage = fetch_webpage(current_url)
            if not should_fetch_page(current_url, webpage["last_modified"]):
                continue

            parsed_data = parse_webpage(webpage["html"], current_url)
            result = {
                "body_text": parsed_data["body_text"],
                "last_modified": webpage["last_modified"],
                "parent_url": parent_url,
                "title": parsed_data["title"],
                "url": current_url,
            }
            results.append(result)

            for url in parsed_data["urls"]:
                if url not in visited:
                    queue.append((url, current_url))
        except Exception as e:
            print(f"Failed to fetch {current_url}: {e}")

    return results


def fetch_and_save_pages(base_url: str):
    """
    Fetches webpages starting from the specified base URL and saves them to the database.

    Args:
        base_url (str): The initial URL from which to begin fetching webpages.
    """

    results = recursive_fetch(base_url)
    for result in results:
        add_pages(
            body_text=result["body_text"],
            last_modified=result["last_modified"],
            parent_url=result["parent_url"],
            title=result["title"],
            url=result["url"],
            child_links=result["urls"],
        )
