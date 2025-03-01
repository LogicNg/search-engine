from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


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
    Dict = {}
    Dict["html"] = html_content
    Dict["last_modified"] = last_modified
    return Dict
    # raise NotImplementedError("This function is not implemented yet.")


def parse_webpage(html: str) -> Dict[str, Optional[object]]:
    """
    Parses the webpage HTML to extract the title, body text, and all URLs.

    Args:
        html (str): The HTML content of the webpage.

    Returns:
        Dict[str, Optional[object]]: A dictionary containing:
            - "title" (str): The title of the webpage, or None if not found.
            - "body_text" (str): The combined text of the body content.
            - "urls" (List[str]): A list of all URLs found in anchor tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else None
    body_text = " ".join(p.get_text() for p in soup.find_all("p"))
    urls = [a["href"] for a in soup.find_all("a", href=True)]
    Dict = {}
    Dict["title"] = title
    Dict["body_text"] = body_text
    Dict["urls"] = urls
    return Dict
    # raise NotImplementedError("This function is not implemented yet.")


def recursive_fetch(base_url: str):
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
    raise NotImplementedError()


if __name__ == "__main__":
    res = fetch_webpage("https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm")
    print(res["last_modified"])
    print(parse_webpage(res["html"]))
