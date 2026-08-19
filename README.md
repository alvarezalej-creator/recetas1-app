# recetas1-app

Gestor de recetas de cocina (CLI + web Flask), MVC, SQLite. Ver
`specs/SPEC.md` y `specs/PLAN.md`.

## Uso

```bash
uv sync
uv run python main.py      # CLI interactiva
uv run python app.py       # app web (Flask)
uv run pytest              # pruebas de la capa de modelos
```

## Novedades v2
- **Favoritos**: marca/desmarca una receta (opción 8 en la CLI, botón ★/☆ en
  la web) y filtra listados/búsquedas por "solo favoritas".
- **Lista de la compra**: genera la lista de ingredientes de una receta
  (opción 9 en la CLI, enlace "Lista de la compra" en el detalle/listado web).