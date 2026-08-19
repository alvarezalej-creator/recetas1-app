import os

from flask import Flask, redirect, url_for
from flask.typing import ResponseReturnValue

from models.category import CategoryModel
from models.database import Database
from models.recipe import RecipeModel
from web.routes.categories import create_categories_blueprint
from web.routes.recipes import create_recipes_blueprint


def create_app(db_path: str = "data/recetas.db") -> Flask:
    """Crea y configura la app Flask del Gestor de Recetas."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-insecure-secret-key")

    database = Database(db_path)
    category_model = CategoryModel(database)
    recipe_model = RecipeModel(database)

    app.register_blueprint(create_recipes_blueprint(recipe_model, category_model))
    app.register_blueprint(create_categories_blueprint(category_model))

    @app.route("/")
    def index() -> ResponseReturnValue:
        return redirect(url_for("recipes.list_recipes"))

    return app
