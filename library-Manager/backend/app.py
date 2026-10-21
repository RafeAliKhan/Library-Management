import os
from flask import Flask, send_from_directory
from db import close_db, init_db
from routes import auth_routes, books, loans

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
app.teardown_appcontext(close_db)
for module in (auth_routes, books, loans):
    app.register_blueprint(module.bp)


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
