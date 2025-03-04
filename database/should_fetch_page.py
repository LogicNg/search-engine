from db import cursor, connection

def should_fetch_page(url: str, last_modified: str):
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

    #Get paeg_id from url_mapping table
    sql = "SELECT page_id FROM url_mapping WHERE url = ?"
    cursor.execute(sql, (url,))
    page_id = cursor.fetchone()

    if page_id is None:
        return True


    sql = "SELECT last_modified_date FROM forward_index WHERE page_id = ?"
    cursor.execute(sql, (page_id[0],))
    result = cursor.fetchone()

    if result[0] == last_modified:
        return False
    else:
        return True
    

    #raise NotImplementedError()

#Test
print(should_fetch_page("https://www.example.com", "Tue, 16 May 2023 05:03:16 GMT")) #True
print(should_fetch_page("https://www.example.com/page1", "Tue, 16 May 2023 05:03:16 GMT")) #False