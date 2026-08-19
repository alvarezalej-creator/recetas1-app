from dataclasses import dataclass
from typing import Optional

from models.database import Database


@dataclass
class Category:
    """Representa una categoría de recetas."""

    id: int
    name: str


class CategoryModel:
    """Acceso a datos para categorías."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def list_all(self) -> list[Category]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name FROM categories ORDER BY name"
            ).fetchall()
            return [Category(id=row["id"], name=row["name"]) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT id, name FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            return Category(id=row["id"], name=row["name"]) if row else None
        finally:
            conn.close()

    def get_by_name(self, name: str) -> Optional[Category]:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT id, name FROM categories WHERE name = ?", (name,)
            ).fetchone()
            return Category(id=row["id"], name=row["name"]) if row else None
        finally:
            conn.close()

    def create(self, name: str) -> Category:
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO categories (name) VALUES (?)", (name,)
            )
            conn.commit()
            category_id = cursor.lastrowid
            assert category_id is not None
            return Category(id=category_id, name=name)
        finally:
            conn.close()

    def get_or_create(self, name: str) -> Category:
        existing = self.get_by_name(name)
        if existing is not None:
            return existing
        return self.create(name)

    def count_recipes(self, category_id: int) -> int:
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM recipes WHERE category_id = ?",
                (category_id,),
            ).fetchone()
            return int(row["total"])
        finally:
            conn.close()
