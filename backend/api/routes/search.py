import math

from flask import Blueprint, jsonify, request

from api.get_cursor import get_cursor

search_bp = Blueprint("search", __name__)

"""
# Sample result
pages = [
    {
        "score": 0.99999,
        "title": "Home Move (2001) sfasdfasdfsadfasdfasdfas",
        "link": "https://www.cse.hk.hk/alumni/2016-06-08",
        "last_modification_date": "2016-06-16T00:00:00Z",
        "file_size": "5931B",
        "keywords": {"CSE": "3", "MOV": "5", "TEST": "4"},
        "children_links": [
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
        ],
        "parent_links": [
            "http://parentlink1.com",
            "http://parentlink2.com",
            "http://parentlink3.com",
        ],
    },
    {
        "score": 0.87654,
        "title": "Home Research Paper on AI (2023)",
        "link": "https://ai-research.org/papers/2023",
        "last_modification_date": "2023-11-15T14:30:00Z",
        "file_size": "2.4MB",
        "keywords": {"AI": "8", "Machine Learning": "6", "Neural Networks": "5"},
        "children_links": [
            "https://ai-research.org/references/1",
            "https://ai-research.org/references/2",
        ],
        "parent_links": ["https://ai-research.org/main"],
    },
    {
        "score": 0.25,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": {"Recipes": "10", "Cooking": "7", "Food": "5"},
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts",
        ],
        "parent_links": ["https://food-blog.com"],
    },
    {
        "score": 0.55,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": {"Recipes": "10", "Cooking": "7", "Food": "5"},
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts",
        ],
        "parent_links": ["https://food-blog.com"],
    },
    {
        "score": 0.98765,
        "title": "Home Annual Financial Report 2022",
        "link": "https://company.com/financials/2022",
        "last_modification_date": "2023-03-01T09:00:00Z",
        "file_size": "5.7MB",
        "keywords": {"Finance": "12", "Report": "8", "2022": "5"},
        "children_links": [],
        "parent_links": ["https://company.com/financials"],
    },
    {
        "score": 0.01,
        "title": "Travel Guide: Japan 2021",
        "link": "https://travel-site.com/japan-guide",
        "last_modification_date": "2021-05-10T16:45:00Z",
        "file_size": "3.1MB",
        "keywords": {"Japan": "15", "Travel": "10", "Guide": "7"},
        "children_links": [
            "https://travel-site.com/japan/hotels",
            "https://travel-site.com/japan/transport",
        ],
        "parent_links": [
            "https://travel-site.com/guides",
            "https://travel-site.com/asia",
        ],
    },
]
"""


def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance (edit distance) between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        int: The minimum number of single-character edits needed to change one string into the other
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_cosine_similarity(
    query_tokens, doc_vector, query_magnitude, token_similarities, enable_fuzzy
):
    """
    Calculate cosine similarity between query and document vectors with fuzzy matching support.

    Args:
        query_tokens: List of tokens in the search query
        doc_vector: Dictionary of document terms and their weights
        query_magnitude: Magnitude of the query vector
        token_similarities: Dictionary mapping query tokens to similar terms
        enable_fuzzy: Whether to use fuzzy matching

    Returns:
        float: Cosine similarity score
    """
    if not doc_vector:
        return 0

    doc_magnitude = math.sqrt(sum(v * v for v in doc_vector.values()))
    if doc_magnitude == 0:
        return 0

    dot_product = 0
    # For each query token, find the best matching document token
    for q_token in query_tokens:
        best_match_score = 0

        # Check exact match first
        if q_token in doc_vector:
            best_match_score = doc_vector[q_token]
        elif enable_fuzzy:
            # Check fuzzy matches
            for doc_token in doc_vector:
                if doc_token in token_similarities.get(q_token, {}):
                    similarity = token_similarities[q_token][doc_token]
                    match_score = doc_vector[doc_token] * similarity
                    best_match_score = max(best_match_score, match_score)

        dot_product += best_match_score

    return dot_product / (doc_magnitude * query_magnitude)


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size string (e.g., "5.7MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"


def get_expanded_tokens(query_tokens, cursor, fuzzy_threshold, enable_fuzzy):
    """
    Get expanded tokens with fuzzy matching if enabled.

    Args:
        query_tokens: Original query tokens
        cursor: Database cursor
        fuzzy_threshold: Maximum edit distance for fuzzy matches
        enable_fuzzy: Whether to use fuzzy matching

    Returns:
        tuple: (expanded_tokens, token_similarities)
    """
    expanded_tokens = set(query_tokens)
    token_similarities = {}  # Store similarity scores for expanded tokens

    if not enable_fuzzy:
        return list(expanded_tokens), token_similarities

    # Get all words from the tokens table for fuzzy matching
    cursor.execute("SELECT word FROM tokens")
    all_words = [row[0] for row in cursor.fetchall()]

    # For each token in the query, find similar words
    for token in query_tokens:
        token_similarities[token] = {}  # Initialize similarity dict for token

        for word in all_words:
            if word == token:
                token_similarities[token][word] = 1.0  # Exact match has similarity 1.0
                continue

            distance = levenshtein_distance(token, word)
            if distance <= fuzzy_threshold:
                # Calculate similarity score (1.0 for exact match, decreasing as distance increases)
                similarity = 1.0 - (distance / (fuzzy_threshold + 1))
                expanded_tokens.add(word)
                token_similarities[token][word] = similarity

    return list(expanded_tokens), token_similarities


def get_document_vector(cursor, url, expanded_tokens, vector_type):
    """
    Get document vector based on term frequency or TF-IDF.

    Args:
        cursor: Database cursor
        url: Document URL
        expanded_tokens: List of query tokens with expansions
        vector_type: Either 'title' for TF-IDF or 'body' for term frequency

    Returns:
        dict: Document vector mapping terms to weights
    """
    placeholders = ",".join(["?"] * len(expanded_tokens))

    if vector_type == "title":
        query = f"""
            SELECT word, tf_idf
            FROM keyword_statistics
            WHERE url = ? AND word IN ({placeholders})
        """
    else:  # body
        query = f"""
            SELECT word, term_frequency
            FROM inverted_index
            WHERE url = ? AND word IN ({placeholders})
        """

    cursor.execute(query, [url] + expanded_tokens)
    return {word: weight for word, weight in cursor.fetchall()}


def get_document_metadata(cursor, url):
    """
    Get metadata for a document including keywords, children and parent links.

    Args:
        cursor: Database cursor
        url: Document URL

    Returns:
        tuple: (keywords, children_links, parent_links)
    """
    # Get top keywords
    cursor.execute(
        """
        SELECT i.word, i.term_frequency
        FROM inverted_index i
        WHERE i.url = ?
        ORDER BY i.term_frequency DESC
        LIMIT 10
    """,
        (url,),
    )
    keywords = {word: str(freq) for word, freq in cursor.fetchall()}

    # Get children links
    cursor.execute(
        """
        SELECT child_url
        FROM page_relationships
        WHERE parent_url = ?
    """,
        (url,),
    )
    children_links = [row[0] for row in cursor.fetchall()]

    # Get parent links
    cursor.execute(
        """
        SELECT parent_url
        FROM page_relationships
        WHERE child_url = ?
    """,
        (url,),
    )
    parent_links = [row[0] for row in cursor.fetchall()]

    return keywords, children_links, parent_links


@search_bp.route("/search")
def search():
    """
    Search endpoint that returns documents matching the query.

    Query parameters:
        query (str): Search query
        fuzzy_threshold (int, optional): Maximum edit distance for fuzzy matching. Default: 2
        fuzzy (str, optional): Enable fuzzy matching ("true" or "false"). Default: "true"

    Returns:
        JSON: Search results with document metadata
    """
    # Extract and validate query parameters
    query = request.args.get("query", "").lower()
    fuzzy_threshold = int(request.args.get("fuzzy_threshold", "2"))
    enable_fuzzy = request.args.get("fuzzy", "true").lower() == "true"

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Get query tokens
    query_tokens = query.split()
    if not query_tokens:
        return jsonify({"results": []})

    cursor = get_cursor()

    # Get expanded tokens with fuzzy matching if enabled
    expanded_tokens, token_similarities = get_expanded_tokens(
        query_tokens, cursor, fuzzy_threshold, enable_fuzzy
    )

    # Find documents matching any token
    placeholders = ",".join(["?"] * len(expanded_tokens))
    cursor.execute(
        f"""
            SELECT DISTINCT f.url, f.title, f.last_modified_date, f.size, p.rank
            FROM forward_index f
            JOIN page_rank p ON f.url = p.url
            JOIN inverted_index i ON f.url = i.url
            WHERE i.word IN ({placeholders})
        """,
        expanded_tokens,
    )

    documents = cursor.fetchall()
    results = []

    # Create query vector (binary: 1 if term is present)
    query_vector = {token: 1 for token in query_tokens}
    query_magnitude = math.sqrt(len(query_tokens))  # Since all weights are 1

    for doc in documents:
        url, title, last_modified, size, page_rank = doc

        # Calculate title and body similarity scores
        title_vector = get_document_vector(cursor, url, expanded_tokens, "title")
        body_vector = get_document_vector(cursor, url, expanded_tokens, "body")

        title_cos_sim = calculate_cosine_similarity(
            query_tokens,
            title_vector,
            query_magnitude,
            token_similarities,
            enable_fuzzy,
        )

        body_cos_sim = calculate_cosine_similarity(
            query_tokens, body_vector, query_magnitude, token_similarities, enable_fuzzy
        )

        # Calculate final score using the formula:
        # (0.7 * CosSim(d_t,Q) + 0.3 * CosSim(d_b,Q)) * PageRank(d)
        final_score = (0.7 * title_cos_sim + 0.3 * body_cos_sim) * page_rank

        # Skip documents with very low scores
        if final_score < 0.01:
            continue

        # Get document metadata
        keywords, children_links, parent_links = get_document_metadata(cursor, url)

        # Create result object
        result = {
            "score": final_score,
            "title": title,
            "link": url,
            "last_modification_date": last_modified,
            "file_size": format_file_size(size),
            "keywords": keywords,
            "children_links": children_links,
            "parent_links": parent_links,
        }

        results.append(result)

    # Sort results by score in descending order and return top 10
    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"results": results[:10]})
