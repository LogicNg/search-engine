from flask import Flask, jsonify, request
from flask_cors import CORS

from api.routes.history import history_bp
from api.routes.search import search_bp
from api.routes.suggestions import suggestions_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(search_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(history_bp)
