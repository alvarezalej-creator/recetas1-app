from dataclasses import dataclass, field
from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from werkzeug.datastructures import ImmutableMultiDict

from models.category import CategoryModel
from models.recipe import Ingredient, RecipeModel, Step


@dataclass
class RecipeFormData:
    """Reconstrucción de lo que el usuario tipeó, para re-renderizar el form."""

    name: str = ""
    description: str = ""
    category_name: str = ""
    prep_time_minutes: str = ""
    servings: str = ""
    ingredients: list[dict[str, str]] = field(default_factory=list)
    steps: list[dict[str, str]] = field(default_factory=list)


def _parse_positive_int(raw: str, field_label: str, errors: list[str]) -> Optional[int]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        errors.append(f"{field_label} debe ser un número entero.")
        return None
    if value <= 0:
        errors.append(f"{field_label} debe ser un número entero positivo.")
        return None
    return value


@dataclass
class ParsedRecipeForm:
    """Resultado de parsear y validar un submit del formulario de receta."""

    form_data: RecipeFormData
    ingredients: list[Ingredient]
    steps: list[Step]
    prep_time_minutes: Optional[int]
    servings: Optional[int]
    errors: list[str]


def _parse_recipe_form(form: "ImmutableMultiDict[str, str]") -> ParsedRecipeForm:
    errors: list[str] = []

    name = form.get("name", "").strip()
    if not name:
        errors.append("El nombre es obligatorio.")

    prep_time_raw = form.get("prep_time_minutes", "")
    servings_raw = form.get("servings", "")
    prep_time_minutes = _parse_positive_int(
        prep_time_raw, "El tiempo de preparación", errors
    )
    servings = _parse_positive_int(servings_raw, "Las porciones", errors)

    ingredient_names = form.getlist("ingredient_name[]")
    ingredient_quantities = form.getlist("ingredient_quantity[]")
    ingredient_units = form.getlist("ingredient_unit[]")
    ingredients: list[Ingredient] = []
    ingredient_rows: list[dict[str, str]] = []
    for i, raw_name in enumerate(ingredient_names):
        raw_name = raw_name.strip()
        quantity = ingredient_quantities[i].strip() if i < len(ingredient_quantities) else ""
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else ""
        if not raw_name:
            continue
        ingredients.append(Ingredient(name=raw_name, quantity=quantity or None, unit=unit or None))
        ingredient_rows.append({"name": raw_name, "quantity": quantity, "unit": unit})
    if not ingredients:
        errors.append("Debes añadir al menos un ingrediente.")

    step_descriptions = form.getlist("step_description[]")
    steps: list[Step] = []
    step_rows: list[dict[str, str]] = []
    for description in step_descriptions:
        description = description.strip()
        if not description:
            continue
        steps.append(Step(order_index=len(steps) + 1, description=description))
        step_rows.append({"description": description})
    if not steps:
        errors.append("Debes añadir al menos un paso.")

    form_data = RecipeFormData(
        name=name,
        description=form.get("description", "").strip(),
        category_name=form.get("category_name", "").strip(),
        prep_time_minutes=prep_time_raw,
        servings=servings_raw,
        ingredients=ingredient_rows,
        steps=step_rows,
    )
    return ParsedRecipeForm(
        form_data=form_data,
        ingredients=ingredients,
        steps=steps,
        prep_time_minutes=prep_time_minutes,
        servings=servings,
        errors=errors,
    )


def create_recipes_blueprint(
    recipe_model: RecipeModel, category_model: CategoryModel
) -> Blueprint:
    bp = Blueprint("recipes", __name__, url_prefix="/recipes")

    @bp.route("", methods=["GET"])
    def list_recipes() -> ResponseReturnValue:
        field = request.args.get("field", "")
        query = request.args.get("q", "").strip()
        category_id_raw = request.args.get("category_id", "")
        only_favorites = request.args.get("favorites", "") == "1"

        if field == "name" and query:
            recipes = recipe_model.search_by_name(query, only_favorites=only_favorites)
        elif field == "ingredient" and query:
            recipes = recipe_model.search_by_ingredient(query, only_favorites=only_favorites)
        elif field == "category" and category_id_raw:
            recipes = recipe_model.search_by_category(
                int(category_id_raw), only_favorites=only_favorites
            )
        else:
            recipes = recipe_model.list_all(only_favorites=only_favorites)

        return render_template(
            "recipes/list.html",
            recipes=recipes,
            categories=category_model.list_all(),
            field=field,
            query=query,
            category_id=category_id_raw,
            only_favorites=only_favorites,
        )

    @bp.route("/new", methods=["GET"])
    def new_recipe_form() -> ResponseReturnValue:
        return render_template(
            "recipes/form.html",
            form_data=RecipeFormData(),
            categories=category_model.list_all(),
            form_action=url_for("recipes.create_recipe"),
            is_edit=False,
        )

    @bp.route("/new", methods=["POST"])
    def create_recipe() -> ResponseReturnValue:
        parsed = _parse_recipe_form(request.form)
        if parsed.errors:
            for message in parsed.errors:
                flash(message, "error")
            return (
                render_template(
                    "recipes/form.html",
                    form_data=parsed.form_data,
                    categories=category_model.list_all(),
                    form_action=url_for("recipes.create_recipe"),
                    is_edit=False,
                ),
                400,
            )

        category_id = (
            category_model.get_or_create(parsed.form_data.category_name).id
            if parsed.form_data.category_name
            else None
        )
        recipe = recipe_model.create(
            name=parsed.form_data.name,
            description=parsed.form_data.description or None,
            category_id=category_id,
            prep_time_minutes=parsed.prep_time_minutes,
            servings=parsed.servings,
            ingredients=parsed.ingredients,
            steps=parsed.steps,
        )
        flash(f"Receta '{recipe.name}' creada.", "success")
        return redirect(url_for("recipes.recipe_detail", recipe_id=recipe.id))

    @bp.route("/<int:recipe_id>", methods=["GET"])
    def recipe_detail(recipe_id: int) -> ResponseReturnValue:
        recipe = recipe_model.get_by_id(recipe_id)
        if recipe is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
            return redirect(url_for("recipes.list_recipes"))
        return render_template("recipes/detail.html", recipe=recipe)

    @bp.route("/<int:recipe_id>/edit", methods=["GET"])
    def edit_recipe_form(recipe_id: int) -> ResponseReturnValue:
        recipe = recipe_model.get_by_id(recipe_id)
        if recipe is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
            return redirect(url_for("recipes.list_recipes"))

        form_data = RecipeFormData(
            name=recipe.name,
            description=recipe.description or "",
            category_name=recipe.category_name or "",
            prep_time_minutes=str(recipe.prep_time_minutes) if recipe.prep_time_minutes else "",
            servings=str(recipe.servings) if recipe.servings else "",
            ingredients=[
                {
                    "name": ingredient.name,
                    "quantity": ingredient.quantity or "",
                    "unit": ingredient.unit or "",
                }
                for ingredient in recipe.ingredients
            ],
            steps=[{"description": step.description} for step in recipe.steps],
        )
        return render_template(
            "recipes/form.html",
            form_data=form_data,
            categories=category_model.list_all(),
            form_action=url_for("recipes.update_recipe", recipe_id=recipe_id),
            is_edit=True,
        )

    @bp.route("/<int:recipe_id>/edit", methods=["POST"])
    def update_recipe(recipe_id: int) -> ResponseReturnValue:
        existing = recipe_model.get_by_id(recipe_id)
        if existing is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
            return redirect(url_for("recipes.list_recipes"))

        parsed = _parse_recipe_form(request.form)
        if parsed.errors:
            for message in parsed.errors:
                flash(message, "error")
            return (
                render_template(
                    "recipes/form.html",
                    form_data=parsed.form_data,
                    categories=category_model.list_all(),
                    form_action=url_for("recipes.update_recipe", recipe_id=recipe_id),
                    is_edit=True,
                ),
                400,
            )

        category_id = (
            category_model.get_or_create(parsed.form_data.category_name).id
            if parsed.form_data.category_name
            else None
        )
        recipe_model.update(
            recipe_id=recipe_id,
            name=parsed.form_data.name,
            description=parsed.form_data.description or None,
            category_id=category_id,
            prep_time_minutes=parsed.prep_time_minutes,
            servings=parsed.servings,
            ingredients=parsed.ingredients,
            steps=parsed.steps,
        )
        flash("Receta actualizada.", "success")
        return redirect(url_for("recipes.recipe_detail", recipe_id=recipe_id))

    @bp.route("/<int:recipe_id>/favorite", methods=["POST"])
    def toggle_favorite(recipe_id: int) -> ResponseReturnValue:
        recipe = recipe_model.toggle_favorite(recipe_id)
        if recipe is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
        else:
            estado = "marcada como favorita" if recipe.is_favorite else "desmarcada como favorita"
            flash(f"Receta '{recipe.name}' {estado}.", "success")
        next_url = request.form.get("next") or url_for("recipes.recipe_detail", recipe_id=recipe_id)
        return redirect(next_url)

    @bp.route("/<int:recipe_id>/shopping-list", methods=["GET"])
    def shopping_list(recipe_id: int) -> ResponseReturnValue:
        recipe = recipe_model.get_by_id(recipe_id)
        if recipe is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
            return redirect(url_for("recipes.list_recipes"))
        ingredients = recipe_model.get_shopping_list(recipe_id) or []
        return render_template(
            "recipes/shopping_list.html", recipe=recipe, ingredients=ingredients
        )

    @bp.route("/<int:recipe_id>/delete", methods=["POST"])
    def delete_recipe(recipe_id: int) -> ResponseReturnValue:
        existing = recipe_model.get_by_id(recipe_id)
        if existing is None:
            flash(f"No existe ninguna receta con id {recipe_id}.", "error")
        else:
            recipe_model.delete(recipe_id)
            flash("Receta eliminada.", "success")
        return redirect(url_for("recipes.list_recipes"))

    return bp
