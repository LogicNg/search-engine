from flask import Blueprint, jsonify

suggestions_bp = Blueprint("suggestions", __name__)

suggestion_list = ["Movie", "Move", "Movement", "Movvvy", "Move", "Movement", "Movvvy"]


@suggestions_bp.route("/suggestions")
def suggestions():
    return jsonify(suggestion_list)
