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
    """Calculate the Levenshtein distance between two strings."""
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


@search_bp.route("/search")
def search():
    query = request.args.get("query", "").lower()
    fuzzy_threshold = int(
        request.args.get("fuzzy_threshold", "2")
    )  # Default edit distance threshold
    enable_fuzzy = request.args.get("fuzzy", "true").lower() == "true"

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Get query tokens
    query_tokens = query.split()

    if not query_tokens:
        return jsonify({"results": []})

    cursor = get_cursor()

    # Get expanded tokens with fuzzy matching if enabled
    expanded_tokens = set(query_tokens)
    token_similarities = {}  # Store similarity scores for expanded tokens

    if enable_fuzzy:
        # Get all words from the tokens table for fuzzy matching
        cursor.execute("SELECT word FROM tokens")
        all_words = [row[0] for row in cursor.fetchall()]

        # For each token in the query, find similar words
        for token in query_tokens:
            token_similarities[token] = {}  # Initialize similarity dict for token

            for word in all_words:
                if word == token:
                    token_similarities[token][
                        word
                    ] = 1.0  # Exact match has similarity 1.0
                    continue

                distance = levenshtein_distance(token, word)
                if distance <= fuzzy_threshold:
                    # Calculate similarity score (1.0 for exact match, decreasing as distance increases)
                    similarity = 1.0 - (distance / (fuzzy_threshold + 1))
                    expanded_tokens.add(word)
                    token_similarities[token][word] = similarity

    # Get all documents that match any expanded token
    placeholders = ",".join(["?"] * len(expanded_tokens))
    expanded_tokens_list = list(expanded_tokens)

    cursor.execute(
        f"""
            SELECT DISTINCT f.url, f.title, f.last_modified_date, f.size, p.rank
            FROM forward_index f
            JOIN page_rank p ON f.url = p.url
            JOIN inverted_index i ON f.url = i.url
            WHERE i.word IN ({placeholders})
        """,
        expanded_tokens_list,
    )

    documents = cursor.fetchall()
    results = []

    # Create query vector (binary: 1 if term is present)
    query_vector = {token: 1 for token in query_tokens}
    query_magnitude = math.sqrt(len(query_tokens))  # Since all weights are 1

    for doc in documents:
        url, title, last_modified, size, page_rank = doc

        # Get document title vector based on TF-IDF
        title_placeholders = ",".join(["?"] * len(expanded_tokens))
        cursor.execute(
            f"""
                SELECT word, tf_idf
                FROM keyword_statistics
                WHERE url = ? AND word IN ({title_placeholders})
            """,
            [url] + expanded_tokens_list,
        )

        # Create document title vector
        title_vector = {word: tfidf for word, tfidf in cursor.fetchall()}
        title_magnitude = math.sqrt(sum(v * v for v in title_vector.values()))

        # Calculate cosine similarity for title with fuzzy matching
        if title_magnitude > 0:
            dot_product = 0

            # For each query token, find the best matching document token
            for q_token in query_tokens:
                best_match_score = 0

                # Check exact match first
                if q_token in title_vector:
                    best_match_score = title_vector[q_token]
                elif enable_fuzzy:
                    # Check fuzzy matches
                    for doc_token in title_vector:
                        if doc_token in token_similarities.get(q_token, {}):
                            similarity = token_similarities[q_token][doc_token]
                            match_score = title_vector[doc_token] * similarity
                            best_match_score = max(best_match_score, match_score)

                dot_product += best_match_score

            title_cos_sim = dot_product / (title_magnitude * query_magnitude)
        else:
            title_cos_sim = 0

        # Get document body vector based on term frequency
        body_placeholders = ",".join(["?"] * len(expanded_tokens))
        cursor.execute(
            f"""
                SELECT word, term_frequency
                FROM inverted_index
                WHERE url = ? AND word IN ({body_placeholders})
            """,
            [url] + expanded_tokens_list,
        )

        # Create document body vector
        body_vector = {word: tf for word, tf in cursor.fetchall()}
        body_magnitude = math.sqrt(sum(v * v for v in body_vector.values()))

        # Calculate cosine similarity for body with fuzzy matching
        if body_magnitude > 0:
            dot_product = 0

            # For each query token, find the best matching document token
            for q_token in query_tokens:
                best_match_score = 0

                # Check exact match first
                if q_token in body_vector:
                    best_match_score = body_vector[q_token]
                elif enable_fuzzy:
                    # Check fuzzy matches
                    for doc_token in body_vector:
                        if doc_token in token_similarities.get(q_token, {}):
                            similarity = token_similarities[q_token][doc_token]
                            match_score = body_vector[doc_token] * similarity
                            best_match_score = max(best_match_score, match_score)

                dot_product += best_match_score

            body_cos_sim = dot_product / (body_magnitude * query_magnitude)
        else:
            body_cos_sim = 0

        # Calculate final score using the formula:
        # (0.7 * CosSim(d_t,Q) + 0.3 * CosSim(d_b,Q)) * PageRank(d_t)
        final_score = (0.7 * title_cos_sim + 0.3 * body_cos_sim) * page_rank

        # Skip documents with very low scores
        if final_score < 0.01:
            continue

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

        # Format file size
        if size < 1024:
            file_size = f"{size}B"
        elif size < 1024 * 1024:
            file_size = f"{size/1024:.1f}KB"
        else:
            file_size = f"{size/(1024*1024):.1f}MB"

        # Create result object
        result = {
            "score": final_score,
            "title": title,
            "link": url,
            "last_modification_date": last_modified,
            "file_size": file_size,
            "keywords": keywords,
            "children_links": children_links,
            "parent_links": parent_links,
        }

        results.append(result)

    # Sort results by score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)

    # Return top results
    return jsonify({"results": results[:10]})
