from flask import Blueprint, jsonify, request

from api.utils.levenshtein_distance import levenshtein_distance
from api.utils.get_cursor import get_cursor

suggestions_bp = Blueprint("suggestions", __name__)


@suggestions_bp.route("/suggestions")
def suggestions():
    """
    Provides query autosuggestions based on the user's input.

    This endpoint returns a list of suggested search terms that begin with
    the characters the user has typed. It prioritizes single words over phrases
    and more frequently occurring terms in the indexed documents.

    Request parameters:
        q (str): The partial query string to generate suggestions for
        fuzzy (str, optional): Enable fuzzy matching ("true" or "false"). Default: "false"
        threshold (int, optional): Maximum edit distance for fuzzy matches. Default: 2

    Returns:
        JSON array: Up to 10 suggested search terms sorted by relevance.
        Returns an empty array if no query parameter is provided or no
        matches are found.
    """
    # Get query parameters
    query = request.args.get("query", "").lower().strip()
    enable_fuzzy = request.args.get("fuzzy", "false").lower() == "true"
    threshold = int(request.args.get("threshold", "2"))

    if not query:
        return jsonify([])

    # Get database cursor
    cursor = get_cursor()

    suggestions = []

    # First try exact prefix matches (current implementation)
    cursor.execute(
        """
        SELECT t.word 
        FROM tokens t
        LEFT JOIN inverted_index i ON t.word = i.word
        WHERE t.word LIKE ? 
        GROUP BY t.word
        ORDER BY t.ngram_size, SUM(COALESCE(i.term_frequency, 0)) DESC
        LIMIT 10
    """,
        (query + "%",),
    )

    exact_suggestions = [row[0] for row in cursor.fetchall()]
    suggestions.extend(exact_suggestions)

    # If fuzzy matching is enabled and we need more suggestions
    if enable_fuzzy and len(suggestions) < 10:
        # Get all words from the tokens table
        cursor.execute(
            """
            SELECT t.word, SUM(COALESCE(i.term_frequency, 0)) as freq, t.ngram_size
            FROM tokens t
            LEFT JOIN inverted_index i ON t.word = i.word
            WHERE t.word NOT LIKE ?
            GROUP BY t.word
            """,
            (query + "%",),  # Exclude words we already have
        )

        potential_matches = []
        for row in cursor.fetchall():
            word, freq, ngram_size = row
            # Calculate edit distance
            distance = levenshtein_distance(
                query, word[: len(query)] if len(word) > len(query) else word
            )
            if distance <= threshold:
                # Add to potential matches with score based on distance and frequency
                score = freq / (
                    distance + 1
                )  # Higher score for closer matches with higher frequency
                potential_matches.append((word, score, ngram_size))

        # Sort by ngram_size and then score
        potential_matches.sort(key=lambda x: (x[2], -x[1]))

        # Add fuzzy matches until we have 10 suggestions
        fuzzy_suggestions = [
            match[0] for match in potential_matches[: 10 - len(suggestions)]
        ]
        suggestions.extend(fuzzy_suggestions)

    return jsonify(suggestions[:10])  # Limit to 10 suggestions
