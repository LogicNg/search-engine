import json
from collections import defaultdict
from datetime import datetime

from database.db import connection, cursor
from database.indexer import Indexer

indexer = Indexer()


def insert_url(url):
    """Insert a URL into the urls table if it doesn't already exist."""
    cursor.execute("INSERT OR IGNORE INTO urls (url) VALUES (?)", (url,))


def insert_forward_index(url, title, last_modified, size):
    """Insert or update a page's metadata into the forward_index table."""
    cursor.execute(
        """
        INSERT INTO forward_index (url, title, last_modified_date, size)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            last_modified_date=excluded.last_modified_date,
            size=excluded.size
        """,
        (url, title, last_modified, size),
    )


def insert_page_relationship(parent_url, child_url):
    """Insert a parent-child relationship into the page_relationships table if it doesn't already exist."""
    if parent_url:
        insert_url(parent_url)
        cursor.execute(
            """
            INSERT OR IGNORE INTO page_relationships (parent_url, child_url)
            VALUES (?, ?)
            """,
            (parent_url, child_url),
        )


def calculate_term_frequency(stems):
    """Calculate the term frequency for a list of stems."""
    term_frequency = defaultdict(int)
    for stem in stems:
        term_frequency[stem] += 1
    return term_frequency


def insert_words_and_inverted_index(url, term_frequency):
    """Insert words and their term frequencies into the words and inverted_index tables."""
    for stem, tf in term_frequency.items():
        # Insert into words table
        cursor.execute("INSERT OR IGNORE INTO words (word) VALUES (?)", (stem,))

        # Insert into inverted_index table
        cursor.execute(
            """
            INSERT INTO inverted_index (word, url, term_frequency)
            VALUES (?, ?, ?)
            ON CONFLICT(word, url) DO UPDATE SET
                term_frequency=excluded.term_frequency
            """,
            (stem, url, tf),
        )


def insert_keyword_statistics(url, term_frequency):
    """Insert TF-IDF values into the keyword_statistics table."""
    for stem, tf in term_frequency.items():
        tf_idf = tf  # Assuming IDF is 1 for simplicity
        cursor.execute(
            """
            INSERT INTO keyword_statistics (word, url, tf_idf)
            VALUES (?, ?, ?)
            ON CONFLICT(word, url) DO UPDATE SET
                tf_idf=excluded.tf_idf
            """,
            (stem, url, tf_idf),
        )


def process_page(page):
    """Process a single page and insert its data into the database."""
    url = page["url"]
    title = page["title"]
    last_modified = datetime.strptime(page["last_modified"], "%a, %d %b %Y %H:%M:%S %Z")
    parent_url = page["parent_url"]
    body_text = page["body_text"]
    size = len(body_text)

    # Insert URL and forward index
    insert_url(url)
    insert_forward_index(url, title, last_modified, size)

    # Insert page relationship if parent_url exists
    insert_page_relationship(parent_url, url)

    # Index the page content
    indexer.index_page(url, title, body_text)

    # Get the indexed data
    title_stems = indexer.stem(indexer.tokenize(title))
    body_stems = indexer.stem(indexer.tokenize(body_text))

    # Combine title and body stems
    all_stems = title_stems + body_stems

    # Calculate term frequency
    term_frequency = calculate_term_frequency(all_stems)

    # Insert words and inverted index
    insert_words_and_inverted_index(url, term_frequency)

    # Insert keyword statistics
    insert_keyword_statistics(url, term_frequency)


def add_pages(pages: list[dict]):
    """
    Add multiple webpages to the database.

    Args:
        pages (list[dict]): A list of dictionaries, each containing the following keys:
            - body_text (str): The main content of the page to be added.
            - last_modified (str): The last modified date of the page in the format:
                                   "Tue, 16 May 2023 05:03:16 GMT" (as per RFC 7231).
            - parent_url (str | None): The URL of the parent page, if applicable.
                                       This can be None if there is no parent.
            - title (str): The title of the page to be added.
            - url (str): The URL of the page to be added.

    Returns:
        None: This function does not return any value.
    """
    for page in pages:
        process_page(page)

    connection.commit()
