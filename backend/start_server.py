from api.app import app
from api.routes.history import history_bp
from api.routes.search import search_bp
from api.routes.suggestions import suggestions_bp

app.register_blueprint(search_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(history_bp)

app.run(debug=True)
