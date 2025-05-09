from api.app import app

# from api.routes.search_logic import search_bp
from api.routes.search import search_bp
from api.routes.suggestions import suggestions_bp
from api.routes.get_stemmed_word import get_stemmed_word_bp


"""
    This script starts the Flask server for the search engine application.
    It imports the necessary modules and registers the blueprints for different routes.
    The server runs in debug mode for development purposes.
    To run the server, execute this script. Ensure that the database and other dependencies
    are properly set up before starting the server.
    Usage:
        python/python3 start_server.py
"""

app.register_blueprint(search_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(get_stemmed_word_bp)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
