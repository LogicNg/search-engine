from datetime import datetime

from database.db import connection, cursor


def should_fetch_page(url: str, last_modified: str) -> bool:
    """
    Determine whether a webpage should be fetched based on its URL and last modified date.

    This function evaluates the necessity of fetching a page based on the following criteria:
    - If the URL does not exist in the database, the function will return True, indicating
      that the page should be fetched.
    - If the URL exists in the database and the `last_modified` date has not changed,
      the function will return False, indicating that there is no need to fetch the page.
    - In all other cases, the function will return True, indicating that the page should
      be fetched.

    Args:
        url (str): The URL of the page to evaluate.
        last_modified (str): The last modified date of the page in the format:
                             "Tue, 16 May 2023 05:03:16 GMT" (as per RFC 7231).

    Returns:
        bool: True if the page should be fetched, False otherwise.
    """
    cursor.execute("SELECT last_modified_date FROM page_information WHERE url = ?", (url,))
    result = cursor.fetchone()

    if result is None:
        # URL does not exist in the database
        return True

    db_last_modified = result[0]
    db_last_modified_date = datetime.strptime(
        db_last_modified, "%a, %d %b %Y %H:%M:%S GMT"
    )
    input_last_modified_date = datetime.strptime(
        last_modified, "%a, %d %b %Y %H:%M:%S GMT"
    )

    if db_last_modified_date == input_last_modified_date:
        # URL exists and last modified date has not changed
        return False

    # URL exists but last modified date has changed
    return True


"""
print(should_fetch_page("https://www.example.com", "Tue, 16 May 2023 05:03:16 GMT")) #True
print(should_fetch_page("https://www.example.com/page1", "Tue, 16 May 2023 05:03:16 GMT")) #False
"""
