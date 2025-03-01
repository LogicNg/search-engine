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
