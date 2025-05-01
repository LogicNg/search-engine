from flask import Blueprint, jsonify
from collections import Counter

suggestions_bp = Blueprint("suggestions", __name__)

suggestion_list = ["Movie", "Move", "Movement", "Movvvy", "Move", "Movement", "Movvvy"]


@suggestions_bp.route("/suggestions")
def suggestions():
    query = request.args.get("query", "").lower().strip()
    
    if not query:
        # Return original full list when no query (maintaining original behavior)
        return jsonify(suggestion_list)
    
    # Case-insensitive filtering of original list
    filtered = [
        suggestion for suggestion in suggestion_list 
        if query in suggestion.lower()
    ]
    
    # Deduplicate while preserving order (optional)
    seen = set()
    deduped = []
    for item in filtered:
        lower_item = item.lower()
        if lower_item not in seen:
            seen.add(lower_item)
            deduped.append(item)
    
    return jsonify(deduped)
