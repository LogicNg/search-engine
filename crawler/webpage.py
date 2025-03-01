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
    raise NotImplementedError("This function is not implemented yet.")


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
    raise NotImplementedError("This function is not implemented yet.")
