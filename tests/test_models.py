from models.recipe import Ingredient, Step


def _make_recipe(recipe_model, category_model, name="Tortilla de patatas"):
    category = category_model.get_or_create("Entrantes")
    return recipe_model.create(
        name=name,
        description="Clásica tortilla española",
        category_id=category.id,
        prep_time_minutes=30,
        servings=4,
        ingredients=[
            Ingredient(name="Patata", quantity="4", unit="unidades"),
            Ingredient(name="Huevo", quantity="6", unit="unidades"),
            Ingredient(name="Aceite de oliva", quantity="200", unit="ml"),
        ],
        steps=[
            Step(order_index=1, description="Pelar y cortar las patatas"),
            Step(order_index=2, description="Freír las patatas"),
            Step(order_index=3, description="Batir los huevos y mezclar"),
        ],
    )


# --- CRUD existente (regresión) -------------------------------------------


def test_create_recipe_defaults_to_not_favorite(recipe_model, category_model):
    recipe = _make_recipe(recipe_model, category_model)
    assert recipe.id is not None
    assert recipe.is_favorite is False


def test_get_by_id_returns_full_recipe(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)
    fetched = recipe_model.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Tortilla de patatas"
    assert len(fetched.ingredients) == 3
    assert len(fetched.steps) == 3


def test_get_by_id_missing_returns_none(recipe_model):
    assert recipe_model.get_by_id(999) is None


def test_update_recipe_changes_fields(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)
    recipe_model.update(
        recipe_id=created.id,
        name="Tortilla de patatas con cebolla",
        description=created.description,
        category_id=created.category_id,
        prep_time_minutes=40,
        servings=6,
    )
    updated = recipe_model.get_by_id(created.id)
    assert updated.name == "Tortilla de patatas con cebolla"
    assert updated.prep_time_minutes == 40
    assert updated.servings == 6


def test_delete_recipe_removes_it_and_its_ingredients(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)
    recipe_model.delete(created.id)
    assert recipe_model.get_by_id(created.id) is None


def test_category_get_or_create_reuses_existing(category_model):
    first = category_model.get_or_create("Postres")
    second = category_model.get_or_create("Postres")
    assert first.id == second.id


# --- Favoritos (v2) ---------------------------------------------------------


def test_toggle_favorite_marks_and_unmarks(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)

    marked = recipe_model.toggle_favorite(created.id)
    assert marked.is_favorite is True

    unmarked = recipe_model.toggle_favorite(created.id)
    assert unmarked.is_favorite is False


def test_toggle_favorite_missing_recipe_returns_none(recipe_model):
    assert recipe_model.toggle_favorite(999) is None


def test_list_all_only_favorites_filters(recipe_model, category_model):
    favorite = _make_recipe(recipe_model, category_model, name="Favorita")
    _make_recipe(recipe_model, category_model, name="No favorita")
    recipe_model.toggle_favorite(favorite.id)

    result = recipe_model.list_all(only_favorites=True)

    assert [r.name for r in result] == ["Favorita"]


def test_search_by_name_only_favorites_filters(recipe_model, category_model):
    favorite = _make_recipe(recipe_model, category_model, name="Tarta favorita")
    _make_recipe(recipe_model, category_model, name="Tarta normal")
    recipe_model.toggle_favorite(favorite.id)

    result = recipe_model.search_by_name("Tarta", only_favorites=True)

    assert [r.name for r in result] == ["Tarta favorita"]


# --- Lista de la compra (v2) ------------------------------------------------


def test_get_shopping_list_returns_ingredients_in_order(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)

    shopping_list = recipe_model.get_shopping_list(created.id)

    assert [i.name for i in shopping_list] == ["Patata", "Huevo", "Aceite de oliva"]
    assert shopping_list[0].quantity == "4"
    assert shopping_list[0].unit == "unidades"


def test_get_shopping_list_missing_recipe_returns_none(recipe_model):
    assert recipe_model.get_shopping_list(999) is None


# --- Foto de receta (URL externa) -------------------------------------------


def test_create_recipe_with_image_url(recipe_model, category_model):
    category = category_model.get_or_create("Postres")
    recipe = recipe_model.create(
        name="Tarta de manzana",
        description=None,
        category_id=category.id,
        prep_time_minutes=None,
        servings=None,
        ingredients=[Ingredient(name="Manzana")],
        steps=[Step(order_index=1, description="Hornear")],
        image_url="https://example.com/tarta.jpg",
    )
    assert recipe.image_url == "https://example.com/tarta.jpg"
    fetched = recipe_model.get_by_id(recipe.id)
    assert fetched.image_url == "https://example.com/tarta.jpg"


def test_create_recipe_without_image_url_defaults_to_none(recipe_model, category_model):
    recipe = _make_recipe(recipe_model, category_model)
    assert recipe.image_url is None


def test_update_recipe_changes_image_url(recipe_model, category_model):
    created = _make_recipe(recipe_model, category_model)
    recipe_model.update(
        recipe_id=created.id,
        name=created.name,
        description=created.description,
        category_id=created.category_id,
        prep_time_minutes=created.prep_time_minutes,
        servings=created.servings,
        image_url="https://example.com/foto.jpg",
    )
    updated = recipe_model.get_by_id(created.id)
    assert updated.image_url == "https://example.com/foto.jpg"
