
from db import cursor, connection
import hashlib
import json

page_ids = []

def add_page(
    body_text: str,
    last_modified: str,
    parent_url: str | None,
    title: str,
    url: str,
):
    """
    Add a webpage to the database.

    This function is responsible for inserting a new page into the database. It does not
    return any value. The function will use the provided parameters to populate the
    database schema accordingly.

    Args:
        body_text (str): The main content of the page to be added.
        last_modified (str): The last modified date of the page in the format:
                             "Tue, 16 May 2023 05:03:16 GMT" (as per RFC 7231).
        parent_url (str | None): The URL of the parent page, if applicable.
                                  This can be None if there is no parent.
        title (str): The title of the page to be added.
        url (str): The URL of the page to be added.

    Returns:
        None: This function does not return any value.

    Notes:
        Check the database schema to know what fields to insert.
    """

    # Hash the URL to generate a unique identifier for the page
    page_id = hashlib.md5(url.encode()).hexdigest()
    page_id = int(page_id[:8], 16)
    print(page_id)

    if page_id in page_ids:
        return
    
    page_ids.append(page_id)

    try:
        #Insert the page into the url_mapping table
        sql = "INSERT INTO url_mapping (page_id, url) VALUES (?, ?)"
        cursor.execute(sql, (page_id, url))

        #Get the parent page id from table url_mapping
        sql = "SELECT page_id FROM url_mapping WHERE url = ?"
        cursor.execute(sql, (parent_url,))
        parent_page_id = cursor.fetchone()

        if parent_page_id is not None:
            parent_page_id = parent_page_id[0]
        else:
            parent_page_id = None


        #Insert the page into the forward_index table
        sql = "INSERT INTO forward_index (page_id, title, last_modified_date, size, child_links) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql, (page_id, title, last_modified, len(body_text), json.dumps([])))

        #Insert the page into the page_relationships table
        sql = "INSERT INTO page_relationships (parent_page_id, child_page_id) VALUES (?, ?)"
        cursor.execute(sql, (parent_page_id, page_id))

        connection.commit()
    
    except Exception as e:
        print(e)
        connection.rollback()
        raise e


add_page(
    body_text="This is the body text of the page.",
    last_modified="Tue, 16 May 2023 05:03:16 GMT",
    parent_url="https://www.example.com/page1",
    title="Example Page",
    url="https://www.example.com/page1",
)