from typing import Dict, Optional
from bs4 import BeautifulSoup
import requests

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
    last_modified = response.headers.get('Last-Modified')
    Dict = {}
    Dict["html"] = html_content
    Dict["last_modified"] = last_modified
    return Dict
    #raise NotImplementedError("This function is not implemented yet.")


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
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else None
    body_text = ' '.join(p.get_text() for p in soup.find_all('p'))
    urls = [a['href'] for a in soup.find_all('a', href=True)]
    Dict = {}
    Dict["title"] = title
    Dict["body_text"] = body_text
    Dict["urls"] = urls
    return Dict
    #raise NotImplementedError("This function is not implemented yet.")
if __name__ == "__main__":
    res = fetch_webpage("https://example.com")
    print(res["last_modified"])
    print(parse_webpage(res["html"]))
