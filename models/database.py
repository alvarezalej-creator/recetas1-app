import sqlite3
from pathlib import Path
from datetime import datetime


class Database:
    """Gestor de base de datos SQLite para recetas."""
    
    def __init__(self, db_path: str = "data/recetas.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Inicializa las tablas de la base de datos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de categorías
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Tabla de recetas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                prep_time_minutes INTEGER,
                servings INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Tabla de ingredientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                quantity TEXT,
                unit TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de pasos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                order_index INTEGER NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)

        self._migrate_add_favorite_column(cursor)
        self._migrate_add_image_url_column(cursor)

        conn.commit()
        conn.close()

    @staticmethod
    def _migrate_add_favorite_column(cursor: sqlite3.Cursor) -> None:
        """Añade recipes.is_favorite si falta (migración idempotente v2)."""
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(recipes)")}
        if "is_favorite" not in columns:
            cursor.execute(
                "ALTER TABLE recipes ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0"
            )

    @staticmethod
    def _migrate_add_image_url_column(cursor: sqlite3.Cursor) -> None:
        """Añade recipes.image_url si falta (migración idempotente, fotos)."""
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(recipes)")}
        if "image_url" not in columns:
            cursor.execute("ALTER TABLE recipes ADD COLUMN image_url TEXT")
