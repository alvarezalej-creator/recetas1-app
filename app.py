import os

from web.app import create_app

app = create_app(os.environ.get("RECETAS_DB_PATH", "data/recetas.db"))

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
