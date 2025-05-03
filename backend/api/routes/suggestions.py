from flask import Blueprint, jsonify, request

from api.get_cursor import get_cursor

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

    Returns:
        JSON array: Up to 10 suggested search terms sorted by relevance.
        Returns an empty array if no query parameter is provided or no
        matches are found.
    """
    # Get query parameter from request
    query = request.args.get("q", "").lower().strip()

    if not query:
        return jsonify([])

    # Get database cursor
    cursor = get_cursor()

    # Query tokens table for words starting with the user input
    # Order by ngram_size to prioritize single words over phrases
    # Then by term frequency to show more commonly used terms first
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

    # Convert results to list
    suggestions = [row[0] for row in cursor.fetchall()]

    return jsonify(suggestions)
