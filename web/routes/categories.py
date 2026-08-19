from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from models.category import CategoryModel


def create_categories_blueprint(category_model: CategoryModel) -> Blueprint:
    bp = Blueprint("categories", __name__, url_prefix="/categories")

    @bp.route("", methods=["GET"])
    def list_categories() -> ResponseReturnValue:
        categories = category_model.list_all()
        rows = [(category, category_model.count_recipes(category.id)) for category in categories]
        return render_template("categories/list.html", rows=rows)

    @bp.route("", methods=["POST"])
    def create_category() -> ResponseReturnValue:
        name = request.form.get("name", "").strip()
        if not name:
            flash("El nombre de la categoría no puede estar vacío.", "error")
        elif category_model.get_by_name(name) is not None:
            flash("Ya existe una categoría con ese nombre.", "error")
        else:
            category_model.create(name)
            flash(f"Categoría '{name}' creada.", "success")
        return redirect(url_for("categories.list_categories"))

    return bp
