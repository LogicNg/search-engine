from api.app import app
#from api.routes.search_logic import search_bp
from api.routes.search import search_bp
from api.routes.suggestions import suggestions_bp

app.register_blueprint(search_bp)
app.register_blueprint(suggestions_bp)

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
