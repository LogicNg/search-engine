from flask import Blueprint, jsonify

history_bp = Blueprint("history", __name__)

history_list = [
    {"query": "Dinosaur Planet", "timestamp": "2023-05-16T05:03:16Z"},
    {"query": "Research", "timestamp": "2023-11-15T14:30:00Z"},
    {"query": "Cooking Recipes", "timestamp": "2022-09-22T08:15:00Z"},
]


@history_bp.route("/history")
def history():
    return jsonify(history_list)
