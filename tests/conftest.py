import pytest

from models.category import CategoryModel
from models.database import Database
from models.recipe import RecipeModel


@pytest.fixture
def db(tmp_path):
    """Database SQLite temporal y aislada, nunca data/recetas.db."""
    return Database(str(tmp_path / "test.db"))


@pytest.fixture
def category_model(db):
    return CategoryModel(db)


@pytest.fixture
def recipe_model(db):
    return RecipeModel(db)
