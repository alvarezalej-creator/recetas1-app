# Plan de implementación — v2 (favoritos + lista de la compra)

Basado en `specs/SPEC.md` (v2), aprobado en Fase 1. Este plan cubre solo el
incremento v2 sobre la app ya existente (CLI + web, MVC, SQLite) — no
reestructura lo que ya funciona.

## 1. Estructura de carpetas

Sin cambios de disposición (se mantiene la estructura plana ya documentada en
`SPEC.md` §6: `models/`, `views/`, `controllers/`, `web/` en la raíz). Se
añade únicamente:

```
recetas1-app/
├── tests/                  # nuevo
│   ├── __init__.py
│   ├── conftest.py         # fixture de Database en SQLite temporal (tmp_path)
│   └── test_models.py      # tests de RecipeModel y CategoryModel
```

No se crea `tests/test_controllers.py` en este incremento (fuera del
requisito pedido: "pruebas unitarias básicas ... para la capa de modelos").

## 2. Orden de desarrollo de los módulos

Cada paso deja la app funcionando (sin romper CLI ni web) antes de pasar al
siguiente.

1. **`pyproject.toml`**
   - `requires-python = ">=3.12"`.
   - Añadir grupo de dependencias de desarrollo: `pytest`.
   - Añadir `[tool.pytest.ini_options]` (`testpaths = ["tests"]`).

2. **`models/database.py`** (capa más baja, todo depende de ella)
   - En `init_db()`, tras crear `recipes`, migración idempotente: si la
     columna `is_favorite` no existe, `ALTER TABLE recipes ADD COLUMN
     is_favorite INTEGER NOT NULL DEFAULT 0` (comprobar con `PRAGMA
     table_info(recipes)` para no fallar en bases ya migradas).

3. **`models/recipe.py`** (depende de 2)
   - `Recipe`: añadir campo `is_favorite: bool = False`.
   - `_row_to_recipe`: mapear la nueva columna.
   - `RecipeModel.list_all(only_favorites: bool = False)` y
     `search_by_name/_by_ingredient/_by_category(..., only_favorites: bool =
     False)`: añadir condición `AND r.is_favorite = 1` cuando aplique
     (reutilizando el `_search` interno con `where` compuesto).
   - `RecipeModel.toggle_favorite(recipe_id: int) -> Optional[Recipe]`: lee
     estado actual, hace `UPDATE recipes SET is_favorite = ? WHERE id = ?`,
     devuelve la receta actualizada o `None` si no existe.
   - `RecipeModel.get_shopping_list(recipe_id: int) -> Optional[list[Ingredient]]`:
     reutiliza `get_by_id` + `_get_ingredients`; `None` si la receta no
     existe. (Puede implementarse como método fino que delega en
     `get_by_id(recipe_id).ingredients` — sin nueva tabla, ver SPEC §3.)

   *(`models/category.py` no cambia — favoritos y lista de compra son solo
   de receta.)*

4. **`tests/` (pytest, sobre el modelo ya extendido)**
   - `conftest.py`: fixture `db` que crea `Database` sobre un `tmp_path /
     "test.db"` por test (aislado, sin tocar `data/recetas.db`).
   - `test_models.py`, casos mínimos:
     - Crear receta → `is_favorite` por defecto `False`.
     - `toggle_favorite` → pasa a `True`, y de nuevo a `False`.
     - `toggle_favorite` con id inexistente → `None`, sin excepción.
     - `list_all(only_favorites=True)` filtra correctamente.
     - `search_by_name(..., only_favorites=True)` filtra correctamente.
     - `get_shopping_list` devuelve los ingredientes esperados (nombre,
       cantidad, unidad) en el orden de inserción.
     - `get_shopping_list` con id inexistente → `None`.
     - CRUD existente (create/get_by_id/update/delete) sigue en verde
       (regresión, no solo lo nuevo).
     - `CategoryModel.get_or_create` sigue en verde (regresión mínima de la
       otra clase de modelo).

5. **CLI: `views/menu_view.py` + `controllers/recipe_controller.py` +
   `main.py`** (depende de 3)
   - `menu_view`: añadir opciones 8/9 al menú impreso; helper para pedir
     "¿Solo favoritas? (s/n)"; formateo de ★ en listado/detalle; formateo de
     la lista de la compra.
   - `recipe_controller.py`: `toggle_favorite_flow()` (pide id, llama al
     modelo, muestra resultado) y `shopping_list_flow()` (pide id, imprime
     ingredientes); `list_recipes`/`search_recipes` ganan el filtro opcional.
   - `main.py`: enruta las opciones `8` y `9` del bucle a los nuevos flujos.

6. **Web: `web/routes/recipes.py` + templates** (depende de 3, en paralelo a 5)
   - Ruta `POST /recipes/<id>/favorite`: toggle, `redirect` de vuelta con
     `flash` de confirmación.
   - Ruta `GET /recipes/<id>/shopping-list`: nueva plantilla
     `web/templates/recipes/shopping_list.html`.
   - `list.html` / `_table.html` / `detail.html`: botón ★/☆, checkbox "solo
     favoritas" en el listado (query param `favorites=1`), enlace a la lista
     de la compra desde el detalle.

7. **`README.md`**: nota breve de las dos funcionalidades nuevas y cómo
   usarlas desde CLI y web (una línea cada una).

## 3. Dependencias necesarias

- Runtime: sin nuevas (siguen `typer`, `flask`).
- Desarrollo: `pytest` (nueva, vía `uv add --dev pytest`).
- Entorno: **uv** no está instalado en este entorno de ejecución — antes de
  Fase 3 hay que instalarlo (`curl -LsSf https://astral.sh/uv/install.sh |
  sh`) o usarlo si ya está disponible en tu máquina. Si no se puede instalar,
  como *fallback* documentado se usaría `python -m venv` + `pip install -e .
  pytest`, manteniendo `pyproject.toml` compatible con `uv` igualmente.

## 4. Riesgos / puntos de atención
- La migración `ALTER TABLE` debe ser idempotente (no romper `data/recetas.db`
  ya existente, que hoy no tiene `is_favorite`).
- `RecipeModel._search` se reutiliza para favoritos: revisar que el `where`
  compuesto con `AND` no rompa `search_by_category` (que ya usa `r.category_id
  = ?` como `where`).
- Los tests deben usar una DB temporal (`tmp_path`), nunca
  `data/recetas.db`.
