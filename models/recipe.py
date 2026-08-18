import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from models.database import Database


@dataclass
class Ingredient:
    """Ingrediente de una receta."""

    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Step:
    """Paso de preparación de una receta."""

    order_index: int
    description: str
    id: Optional[int] = None


@dataclass
class Recipe:
    """Receta completa, con ingredientes y pasos."""

    id: int
    name: str
    description: Optional[str]
    category_id: Optional[int]
    prep_time_minutes: Optional[int]
    servings: Optional[int]
    created_at: str
    updated_at: str
    category_name: Optional[str] = None
    ingredients: list[Ingredient] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)


class RecipeModel:
    """Acceso a datos para recetas, ingredientes y pasos."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def list_all(self) -> list[Recipe]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute(
                """
                SELECT r.*, c.name AS category_name
                FROM recipes r
                LEFT JOIN categories c ON c.id = r.category_id
                ORDER BY r.name
                """
            ).fetchall()
            return [self._row_to_recipe(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                """
                SELECT r.*, c.name AS category_name
                FROM recipes r
                LEFT JOIN categories c ON c.id = r.category_id
                WHERE r.id = ?
                """,
                (recipe_id,),
            ).fetchone()
            if row is None:
                return None
            recipe = self._row_to_recipe(row)
            recipe.ingredients = self._get_ingredients(conn, recipe_id)
            recipe.steps = self._get_steps(conn, recipe_id)
            return recipe
        finally:
            conn.close()

    def create(
        self,
        name: str,
        description: Optional[str],
        category_id: Optional[int],
        prep_time_minutes: Optional[int],
        servings: Optional[int],
        ingredients: list[Ingredient],
        steps: list[Step],
    ) -> Recipe:
        now = datetime.now().isoformat(timespec="seconds")
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO recipes
                    (name, description, category_id, prep_time_minutes,
                     servings, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, category_id, prep_time_minutes, servings, now, now),
            )
            recipe_id = cursor.lastrowid
            assert recipe_id is not None
            self._insert_ingredients(conn, recipe_id, ingredients)
            self._insert_steps(conn, recipe_id, steps)
            conn.commit()
        finally:
            conn.close()
        result = self.get_by_id(recipe_id)
        assert result is not None
        return result

    def update(
        self,
        recipe_id: int,
        name: str,
        description: Optional[str],
        category_id: Optional[int],
        prep_time_minutes: Optional[int],
        servings: Optional[int],
        ingredients: Optional[list[Ingredient]] = None,
        steps: Optional[list[Step]] = None,
    ) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        conn = self.db.get_connection()
        try:
            conn.execute(
                """
                UPDATE recipes
                SET name = ?, description = ?, category_id = ?,
                    prep_time_minutes = ?, servings = ?, updated_at = ?
                WHERE id = ?
                """,
                (name, description, category_id, prep_time_minutes, servings, now, recipe_id),
            )
            if ingredients is not None:
                conn.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
                self._insert_ingredients(conn, recipe_id, ingredients)
            if steps is not None:
                conn.execute("DELETE FROM steps WHERE recipe_id = ?", (recipe_id,))
                self._insert_steps(conn, recipe_id, steps)
            conn.commit()
        finally:
            conn.close()

    def delete(self, recipe_id: int) -> None:
        conn = self.db.get_connection()
        try:
            conn.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            conn.execute("DELETE FROM steps WHERE recipe_id = ?", (recipe_id,))
            conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            conn.commit()
        finally:
            conn.close()

    def search_by_name(self, query: str) -> list[Recipe]:
        return self._search("r.name LIKE ?", f"%{query}%")

    def search_by_ingredient(self, query: str) -> list[Recipe]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute(
                """
                SELECT DISTINCT r.*, c.name AS category_name
                FROM recipes r
                LEFT JOIN categories c ON c.id = r.category_id
                JOIN ingredients i ON i.recipe_id = r.id
                WHERE i.name LIKE ?
                ORDER BY r.name
                """,
                (f"%{query}%",),
            ).fetchall()
            return [self._row_to_recipe(row) for row in rows]
        finally:
            conn.close()

    def search_by_category(self, category_id: int) -> list[Recipe]:
        return self._search("r.category_id = ?", category_id)

    def _search(self, where: str, param: object) -> list[Recipe]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute(
                f"""
                SELECT r.*, c.name AS category_name
                FROM recipes r
                LEFT JOIN categories c ON c.id = r.category_id
                WHERE {where}
                ORDER BY r.name
                """,
                (param,),
            ).fetchall()
            return [self._row_to_recipe(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def _row_to_recipe(row: sqlite3.Row) -> Recipe:
        return Recipe(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            category_id=row["category_id"],
            category_name=row["category_name"],
            prep_time_minutes=row["prep_time_minutes"],
            servings=row["servings"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _get_ingredients(conn: sqlite3.Connection, recipe_id: int) -> list[Ingredient]:
        rows = conn.execute(
            "SELECT id, name, quantity, unit FROM ingredients WHERE recipe_id = ? ORDER BY id",
            (recipe_id,),
        ).fetchall()
        return [
            Ingredient(id=row["id"], name=row["name"], quantity=row["quantity"], unit=row["unit"])
            for row in rows
        ]

    @staticmethod
    def _get_steps(conn: sqlite3.Connection, recipe_id: int) -> list[Step]:
        rows = conn.execute(
            "SELECT id, order_index, description FROM steps "
            "WHERE recipe_id = ? ORDER BY order_index",
            (recipe_id,),
        ).fetchall()
        return [
            Step(id=row["id"], order_index=row["order_index"], description=row["description"])
            for row in rows
        ]

    @staticmethod
    def _insert_ingredients(
        conn: sqlite3.Connection, recipe_id: int, ingredients: list[Ingredient]
    ) -> None:
        for ingredient in ingredients:
            conn.execute(
                "INSERT INTO ingredients (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                (recipe_id, ingredient.name, ingredient.quantity, ingredient.unit),
            )

    @staticmethod
    def _insert_steps(conn: sqlite3.Connection, recipe_id: int, steps: list[Step]) -> None:
        for step in steps:
            conn.execute(
                "INSERT INTO steps (recipe_id, order_index, description) VALUES (?, ?, ?)",
                (recipe_id, step.order_index, step.description),
            )
