import json
import math
from collections import defaultdict
from datetime import datetime

from database.db import connection, cursor
from database.indexer import Indexer

indexer = Indexer()


def insert_url(url):
    """Insert a URL into the urls table if it doesn't already exist."""
    cursor.execute("INSERT OR IGNORE INTO urls (url) VALUES (?)", (url,))


def insert_page_information(url, title, last_modified, size):
    """Insert or update a page's metadata into the forward_index table."""
    cursor.execute(
        """
        INSERT INTO page_information (url, title, last_modified_date, size)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            last_modified_date=excluded.last_modified_date,
            size=excluded.size
        """,
        (url, title, last_modified, size),
    )

def insert_foward_index(url, word):
    """Insert or update a page's title into the forward_index table."""
    cursor.execute(
        """
        INSERT INTO forward_index (url, word)
        VALUES (?, ?)
        ON CONFLICT(url) DO UPDATE SET
            word=excluded.word
        """,
        (url, word),
    )

def insert_title_foward_index(url, title):
    """Insert or update a page's title into the forward_index table."""
    cursor.execute(
        """
        INSERT INTO title_forward_index (url, title)
        VALUES (?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title
        """,
        (url, title),
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


def insert_titles_and_titl_inverted_index(url, term_frequency):
    """Insert words and their term frequencies into the words and inverted_index tables."""
    for stem, tf in term_frequency.items():
        # Insert into words table
        cursor.execute("INSERT OR IGNORE INTO titles (title) VALUES (?)", (stem,))

        # Insert into inverted_index table
        cursor.execute(
            """
            INSERT INTO title_inverted_index (title, url, term_frequency)
            VALUES (?, ?, ?)
            ON CONFLICT(title, url) DO UPDATE SET
                term_frequency=excluded.term_frequency
            """,
            (stem, url, tf),
        )


def get_total_documents():
    """Get the total number of documents in the database."""
    cursor.execute("SELECT COUNT(*) FROM urls")
    return cursor.fetchone()[0]


def get_document_frequency(stem):
    """Get the number of documents in which the term appears."""
    cursor.execute(
        "SELECT COUNT(DISTINCT url) FROM inverted_index WHERE word = ?", (stem,)
    )
    return cursor.fetchone()[0]


def get_title_frequency(stem):
    """Get the number of documents in which the term appears."""
    cursor.execute(
        "SELECT COUNT(DISTINCT url) FROM title_inverted_index WHERE title = ?", (stem,)
    )
    return cursor.fetchone()[0]


def insert_word_statistics(url, term_frequency, max_word_tf):
    """Insert TF-IDF values into the keyword_statistics table."""
    total_documents = get_total_documents()

    for stem, tf in term_frequency.items():
        word_idf = get_document_frequency(stem)
        idf = math.log2(total_documents / word_idf)
        tf_idf = tf * idf / max_word_tf
        cursor.execute(
            """
            INSERT INTO word_statistics (word, url, tf_idf)
            VALUES (?, ?, ?)
            ON CONFLICT(word, url) DO UPDATE SET
                tf_idf=excluded.tf_idf
            """,
            (stem, url, tf_idf),
        )


def insert_title_statistics(url, term_frequency, max_title_tf):
    """Insert TF-IDF values into the title_statistics table."""
    total_documents = get_total_documents()

    for stem, tf in term_frequency.items():
        title_idf = get_title_frequency(stem)
        idf = math.log2(total_documents / title_idf)
        tf_idf = tf * idf / max_title_tf
        cursor.execute(
            """
            INSERT INTO title_statistics (title, url, tf_idf)
            VALUES (?, ?, ?)
            ON CONFLICT(title, url) DO UPDATE SET
                tf_idf=excluded.tf_idf
            """,
            (stem, url, tf_idf),
        )


# Referenced from insert_words_and_inverted_index(url, term_frequencies)
def insert_tokens(url, term_frequencies):
    """Insert words/n-grams and their term frequencies into the tokens"""
    for token_info, tf in term_frequencies.items():
        if isinstance(token_info, tuple):
            # Handle n-gram case where token_info is (token, n)
            token, ngram_size = token_info
        else:
            # Handle single word case
            token = token_info
            ngram_size = 1

        # Insert into tokens table with ngram_size
        cursor.execute(
            "INSERT OR IGNORE INTO tokens (word, ngram_size) VALUES (?, ?)",
            (token, ngram_size),
        )


def generate_ngrams(tokens, n):
    """Generate n-grams from a list of tokens."""
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def process_page(page):
    """Process a single page and insert its data into the database."""
    url = page["url"]
    title = page["title"]
    last_modified = datetime.strptime(page["last_modified"], "%a, %d %b %Y %H:%M:%S %Z")
    # last_modified = datetime.strptime(page["last_modified"], "%Y-%m-%d %H:%M:%S")
    parent_url = page["parent_url"]
    body_text = page["body_text"]
    # size = len(body_text)
    size = page["size"]

    # Insert URL and forward index
    insert_url(url)
    insert_page_information(url, title, last_modified, size)
    insert_foward_index(url, body_text)
    insert_title_foward_index(url, title)

    # Insert page relationship if parent_url exists
    insert_page_relationship(parent_url, url)

    # Index the page content
    indexer.index_page(url, title, body_text)

    # Get the indexed data
    title_stems = indexer.stem(indexer.tokenize(title))
    body_stems = indexer.stem(indexer.tokenize(body_text))

    # Insert title and body into the page_stemmed_word and page_stemmed_title tables
    cursor.execute(
        """INSERT INTO page_stemmed_title (url, stemmed_title) VALUES (?, ?)""",
        (url, " ".join(title_stems)),
    )
    cursor.execute(
        """INSERT INTO page_stemmed_word (url, stemmed_word) VALUES (?, ?)""",
        (url, " ".join(body_stems)),
    )

    # Culate term frequency for title and body
    title_term_frequency = calculate_term_frequency(title_stems)
    body_term_frequency = calculate_term_frequency(body_stems)

    # Insert title words and inverted index, and body words and inverted index
    insert_titles_and_titl_inverted_index(url, title_term_frequency)
    insert_words_and_inverted_index(url, body_term_frequency)

    ###############################################################
    # Here handle token and n-grams

    # Get the tokenized data
    title_tokens = indexer.stem(indexer.tokenize(title))
    body_tokens = indexer.stem(indexer.tokenize(body_text))

    # Calculate term frequencies for all tokens (including n-grams)
    term_frequencies = defaultdict(int)
    all_stems = title_stems + body_stems

    # Add unigrams (single words)
    for stem in all_stems:
        term_frequencies[stem] += 1

    # Generate and add n-grams (for n=2 and n=3)
    for n in [2, 3]:
        # Generate n-grams from title
        if len(title_tokens) >= n:
            title_ngrams = generate_ngrams(title_tokens, n)
            for ngram in title_ngrams:
                term_frequencies[(ngram, n)] += 1

        # Generate n-grams from body
        if len(body_tokens) >= n:
            body_ngrams = generate_ngrams(body_tokens, n)
            for ngram in body_ngrams:
                term_frequencies[(ngram, n)] += 1

    insert_tokens(url, term_frequencies)


def compute_word_and_title_statistics():
    """Compute and insert word and title statistics into the database."""
    cursor.execute("SELECT DISTINCT url FROM urls")
    urls = cursor.fetchall()

    for (url,) in urls:
        # Get the term frequency for the body text from inverted_index
        words_tf = cursor.execute(
            "SELECT word, term_frequency FROM inverted_index WHERE url = ?", (url,)
        ).fetchall()

        # Get the term frequency for the title from title_inverted_index
        titles_tf = cursor.execute(
            "SELECT title, term_frequency FROM title_inverted_index WHERE url = ?",
            (url,),
        ).fetchall()

        # Convert the list of tuples to a dictionary
        words_tf_dict = {word: tf for word, tf in words_tf}
        titles_tf_dict = {title: tf for title, tf in titles_tf}

        # Get maxTF of word for this document
        max_word_tf = max(words_tf_dict.values()) if words_tf_dict else 0
        # Get maxTF of title for this document
        max_title_tf = max(titles_tf_dict.values()) if titles_tf_dict else 0

        # Insert word statistics
        insert_word_statistics(url, words_tf_dict, max_word_tf)
        # Insert title statistics
        insert_title_statistics(url, titles_tf_dict, max_title_tf)


'''
def insert_keyword_statistics(url, term_frequencies):
    """Insert TF-IDF values into the keyword_statistics table."""
    total_documents = get_total_documents()
    for token_info, tf in term_frequencies.items():
        if isinstance(token_info, tuple):
            token = token_info[0]  # Extract token from tuple
        else:
            token = token_info

        document_frequency = get_document_frequency(token)
        if document_frequency > 0:  # Avoid division by zero
            idf = math.log(total_documents / document_frequency)
            tf_idf = tf * idf
            cursor.execute(
                """
                INSERT INTO keyword_statistics (word, url, tf_idf)
                VALUES (?, ?, ?)
                ON CONFLICT(word, url) DO UPDATE SET
                    tf_idf=excluded.tf_idf
                """,
                (token, url, tf_idf),
            )


def process_page(page):
    """Process a single page and insert its data into the database."""
    url = page["url"]
    title = page["title"]
    last_modified = datetime.strptime(page["last_modified"], "%a, %d %b %Y %H:%M:%S %Z")
    parent_url = page["parent_url"]
    body_text = page["body_text"]
    size = page["size"]

    # Insert URL and forward index
    insert_url(url)
    insert_forward_index(url, title, last_modified, size)

    # Insert page relationship if parent_url exists
    insert_page_relationship(parent_url, url)

    # Index the page content
    indexer.index_page(url, title, body_text)

    # Get the tokenized data
    title_tokens = indexer.stem(indexer.tokenize(title))
    body_tokens = indexer.stem(indexer.tokenize(body_text))

    # Process single words (unigrams)
    title_stems = indexer.stem(title_tokens)
    body_stems = indexer.stem(body_tokens)
    all_stems = title_stems + body_stems

    # Calculate term frequencies for all tokens (including n-grams)
    term_frequencies = defaultdict(int)

    # Add unigrams (single words)
    for stem in all_stems:
        term_frequencies[stem] += 1

    # Generate and add n-grams (for n=2 and n=3)
    for n in [2, 3]:
        # Generate n-grams from title
        if len(title_tokens) >= n:
            title_ngrams = generate_ngrams(title_tokens, n)
            for ngram in title_ngrams:
                term_frequencies[(ngram, n)] += 1

        # Generate n-grams from body
        if len(body_tokens) >= n:
            body_ngrams = generate_ngrams(body_tokens, n)
            for ngram in body_ngrams:
                term_frequencies[(ngram, n)] += 1

    # Insert words/n-grams and inverted index
    insert_words_and_inverted_index(url, term_frequencies)

    # Insert keyword statistics
    insert_keyword_statistics(url, term_frequencies)
'''


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
            - size (int): The size of the page.

    Returns:
        None: This function does not return any value.
    """
    for page in pages:
        process_page(page)

    # Compute and insert word and title statistics
    compute_word_and_title_statistics()

    connection.commit()
