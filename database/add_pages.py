import hashlib
import json

from database.db import connection, cursor


def add_pages(pages: list[dict]):
    """
    Add multiple webpages to the database.

    This function is responsible for inserting new pages into the database. It does not
    return any value. The function will use the provided parameters to populate the
    database schema accordingly.

    Args:
        pages (list[dict]): A list of dictionaries, each containing the following keys:
            - body_text (str): The main content of the page to be added.
            - last_modified (str): The last modified date of the page in the format:
                                   "Tue, 16 May 2023 05:03:16 GMT" (as per RFC 7231).
            - parent_url (str | None): The URL of the parent page, if applicable.
                                       This can be None if there is no parent.
            - title (str): The title of the page to be added.
            - url (str): The URL of the page to be added.
            - child_links (list[str]): A list of URLs of the child pages.

    Returns:
        None: This function does not return any value.

    Notes:
        Check the database schema to know what fields to insert.
    """

    url_mapping_data = []
    forward_index_data = []
    page_relationships_data = []

    for page in pages:
        body_text = page["body_text"]
        last_modified = page["last_modified"]
        parent_url = page.get("parent_url")
        title = page["title"]
        child_links = page["child_links"]
        url = page["url"]

        url_mapping_data.append((url,))
        forward_index_data.append(
            (title, last_modified, len(body_text), json.dumps(child_links))
        )

        if parent_url is not None:
            sql = "SELECT page_id FROM url_mapping WHERE url = ?"
            cursor.execute(sql, (parent_url,))
            parent_page_id = cursor.fetchone()
            if parent_page_id is not None:
                parent_page_id = parent_page_id[0]
                page_relationships_data.append(
                    (parent_page_id, None)
                )  # Placeholder for child_page_id
        else:
            page_relationships_data.append((0, None))  # Placeholder for child_page_id

    try:
        # Batch insert into url_mapping table
        cursor.executemany("INSERT INTO url_mapping (url) VALUES (?)", url_mapping_data)
        connection.commit()

        # Retrieve the page_ids for the inserted URLs
        cursor.execute(
            "SELECT page_id, url FROM url_mapping WHERE url IN ({})".format(
                ",".join("?" for _ in url_mapping_data)
            ),
            [url for (url,) in url_mapping_data],
        )
        url_to_page_id = {url: page_id for page_id, url in cursor.fetchall()}

        # Update forward_index_data and page_relationships_data with the correct page_ids
        for i, (title, last_modified, size, child_links) in enumerate(
            forward_index_data
        ):
            page_id = url_to_page_id[url_mapping_data[i][0]]
            forward_index_data[i] = (page_id, title, last_modified, size, child_links)
            page_relationships_data[i] = (page_relationships_data[i][0], page_id)

        # Batch insert into forward_index table
        cursor.executemany(
            "INSERT INTO forward_index (page_id, title, last_modified_date, size, child_links) VALUES (?, ?, ?, ?, ?)",
            forward_index_data,
        )
        connection.commit()

        # Batch insert into page_relationships table
        cursor.executemany(
            "INSERT INTO page_relationships (parent_page_id, child_page_id) VALUES (?, ?)",
            page_relationships_data,
        )
        connection.commit()

    except Exception as e:
        print(e)
        connection.rollback()
        raise e
