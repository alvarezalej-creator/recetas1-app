# Especificación — Gestor de Recetas de Cocina

> **v2**: añade favoritos y lista de la compra (fuera de alcance en v1).
> También aplica a la interfaz web adicional (`web/`), no solo a la CLI.
> Ver marcas «(v2)» en cada sección.
> **v3**: foto de receta vía URL externa (solo interfaz web) y rediseño
> visual (paleta cálida, tarjetas con foto). Ver marcas «(v3)».

## 1. Visión general
Aplicación de recetas de cocina en Python, con dos interfaces sobre el mismo
dominio: **CLI interactiva** (principal) y una **app web con Flask**
(adicional, en `web/`). Ambas permiten crear, consultar, editar, eliminar y
buscar recetas. Los datos se persisten en una base de datos **SQLite** local.

- Interfaz: CLI interactiva (menús numerados, `input()`/`print()`) + web
  Flask (v2: se documenta formalmente aquí, ya estaba implementada).
- Persistencia: SQLite (archivo `data/recetas.db`).
- Arquitectura: **MVC** (Modelo / Vista / Controlador) en carpetas separadas.
- Gestor de entorno y dependencias: **uv**.
- Alcance v1: CRUD completo + búsqueda. Alcance v2: + favoritos + lista de
  la compra.

## 2. Funcionalidades

| # | Funcionalidad | Descripción |
|---|---|---|
| 1 | Añadir receta | Captura nombre, descripción, categoría, tiempo de preparación, porciones, ingredientes (lista) y pasos (lista ordenada). |
| 2 | Listar recetas | Vista resumida: id, nombre, categoría, tiempo de preparación, favorita (★). Admite filtro «solo favoritas» (v2). |
| 3 | Ver detalle de receta | Muestra receta completa: ingredientes con cantidad/unidad, pasos ordenados y estado de favorito. |
| 4 | Editar receta | Permite modificar cualquier campo, incluidos ingredientes y pasos. |
| 5 | Eliminar receta | Solicita confirmación antes de borrar (borra también ingredientes/pasos asociados). |
| 6 | Buscar recetas | Por nombre (coincidencia parcial), por ingrediente, o por categoría. Admite filtro «solo favoritas» (v2). |
| 7 | Gestionar categorías | Listar categorías existentes y crearlas al vuelo al añadir/editar una receta. |
| 8 | Marcar/desmarcar favorito (v2) | Alterna el estado de favorito de una receta existente. |
| 9 | Lista de la compra (v2) | Dada una receta, genera y muestra sus ingredientes agrupados, listos para copiar/imprimir. Vista derivada, no persiste estado (sin "marcar comprado" en v2). |
| 10 | Salir | Cierra la aplicación de forma segura. |

Fuera de alcance en v2 (posibles extensiones futuras): lista de la compra
combinando varias recetas, marcar ítems como comprados de forma persistente,
normalización/conversión de unidades, imágenes, importar/exportar,
multiusuario.

**v3**: se incorpora una foto por receta, solo como **URL externa** (no se
suben archivos al servidor) — campo `image_url` opcional en el formulario
web de alta/edición, mostrado como miniatura en el listado (tarjetas) y como
foto grande en el detalle; placeholder 🍳 si no hay foto. No disponible desde
la CLI (es una funcionalidad de la interfaz web). Además, rediseño visual de
la web: paleta cálida gastronómica, listado en tarjetas en vez de tabla.

## 3. Modelo de datos

### Tabla `categories`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| name | TEXT UNIQUE NOT NULL | Nombre normalizado (sin duplicados) |

### Tabla `recipes`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| name | TEXT NOT NULL | |
| description | TEXT | Opcional |
| category_id | INTEGER FK → categories.id | Nullable |
| prep_time_minutes | INTEGER | Opcional |
| servings | INTEGER | Opcional |
| created_at | TEXT (ISO datetime) | |
| updated_at | TEXT (ISO datetime) | |
| is_favorite | INTEGER NOT NULL DEFAULT 0 | (v2) 0/1. Añadida vía `ALTER TABLE ... ADD COLUMN` idempotente en `Database.init_db()`, compatible con bases ya existentes. |
| image_url | TEXT | (v3) Nullable. URL externa de la foto de la receta; no se almacenan archivos. Misma migración idempotente. |

### Tabla `ingredients`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| recipe_id | INTEGER FK → recipes.id ON DELETE CASCADE | |
| name | TEXT NOT NULL | |
| quantity | TEXT | Texto libre (ej. "2", "1/2") |
| unit | TEXT | Opcional (ej. "tazas", "g") |

### Tabla `steps`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| recipe_id | INTEGER FK → recipes.id ON DELETE CASCADE | |
| order_index | INTEGER NOT NULL | Orden de ejecución del paso |
| description | TEXT NOT NULL | |

Relaciones: `Category 1—N Recipe`, `Recipe 1—N Ingredient`, `Recipe 1—N Step`.
Los borrados de receta eliminan en cascada sus ingredientes y pasos.
La lista de la compra (v2) no crea tablas nuevas: se calcula leyendo
`ingredients` de la receta pedida.

## 4. Pantallas / flujo de la CLI

```
=== Gestor de Recetas ===
1. Añadir receta
2. Listar recetas
3. Ver receta
4. Buscar recetas
5. Editar receta
6. Eliminar receta
7. Gestionar categorías
8. Marcar/desmarcar favorito   (v2)
9. Lista de la compra          (v2)
0. Salir
```

- **Añadir receta**: formulario guiado paso a paso (nombre → categoría →
  descripción → tiempo → porciones → ingredientes en bucle → pasos en bucle).
- **Listar recetas**: tabla simple en texto con id/nombre/categoría/tiempo/★.
  Pregunta opcional "¿Solo favoritas? (s/n)" (v2).
- **Ver receta**: pide un id, muestra la ficha completa incluyendo si es
  favorita.
- **Buscar recetas**: submenú (por nombre / por ingrediente / por categoría),
  reutiliza la vista de listado para mostrar resultados; admite el mismo
  filtro "solo favoritas" (v2).
- **Editar receta**: pide id, muestra valores actuales, permite dejar vacío
  para mantener el valor, permite regenerar ingredientes/pasos.
- **Eliminar receta**: pide id, muestra ficha, pide confirmación (s/n).
- **Gestionar categorías**: listar categorías y su número de recetas; crear
  nueva categoría.
- **Marcar/desmarcar favorito (v2)**: pide id, alterna `is_favorite`,
  confirma el nuevo estado.
- **Lista de la compra (v2)**: pide id de receta, imprime sus ingredientes
  como lista (`- cantidad unidad nombre`).

La interfaz web (Flask, `web/`) ofrece las mismas funcionalidades: listado,
detalle, búsqueda y CRUD de recetas y categorías vía formularios HTML; en v2
añade un botón ★/☆ de favorito en detalle y listado (`POST
/recipes/<id>/favorite`), un checkbox "solo favoritas" en el listado, y una
vista de lista de la compra por receta (`GET /recipes/<id>/shopping-list`).

## 5. Validaciones clave
- El nombre de la receta es obligatorio y no vacío.
- Al añadir/editar, si la categoría no existe se ofrece crearla.
- `prep_time_minutes` y `servings` deben ser enteros positivos si se informan.
- Una receta debe tener al menos 1 ingrediente y 1 paso para guardarse.
- IDs inexistentes en ver/editar/eliminar → mensaje de error controlado, sin
  crash.
- (v2) Toggle de favorito e id inexistente → mismo patrón de error
  controlado.
- (v2) Lista de la compra requiere que la receta tenga ≥1 ingrediente (ya
  garantizado al guardar).

## 6. Arquitectura MVC (estructura de carpetas)

Estructura real del proyecto (plana en la raíz, no bajo `src/`):

```
recetas1-app/
├── pyproject.toml
├── README.md
├── specs/
│   ├── SPEC.md
│   └── PLAN.md
├── main.py                     # entry point CLI (typer)
├── app.py                      # entry point web (Flask dev server)
├── models/
│   ├── __init__.py
│   ├── database.py             # conexión SQLite + esquema (+ migración is_favorite v2)
│   ├── recipe.py               # dataclasses Recipe/Ingredient/Step + acceso a datos
│   └── category.py             # dataclass Category + acceso a datos
├── views/
│   ├── __init__.py
│   └── menu_view.py            # menús y captura de opciones (CLI)
├── controllers/
│   ├── __init__.py
│   ├── recipe_controller.py
│   └── category_controller.py
├── web/                        # interfaz web adicional (Flask)
│   ├── app.py                  # factory create_app()
│   ├── routes/
│   │   ├── recipes.py
│   │   └── categories.py
│   ├── templates/
│   └── static/
├── data/
│   └── recetas.db              # SQLite, no versionado (.gitignore)
└── tests/                      # (v2) no existía; se añade
    └── test_models.py
```

- **Modelo**: acceso a datos (SQLite) y estructuras (`dataclass`). No conoce
  la CLI ni Flask.
- **Vista**: CLI (`views/menu_view.py`, prompts/formateo) o web
  (`web/templates/`, Jinja2). Ninguna conoce SQL.
- **Controlador**: orquesta el flujo, valida y conecta vista con modelo; los
  controladores de `controllers/` los usa la CLI, y `web/routes/` cumple el
  rol de controlador para la web reutilizando los mismos modelos.

## 7. Entorno y dependencias
- Gestión con **uv**: `uv init`, `uv add`, `uv run`.
- Python **3.12+** (v2: sube desde `>=3.9`).
- Dependencias runtime: `typer` (CLI), `flask` (web). Persistencia con
  `sqlite3` de la librería estándar.
- Dependencias de desarrollo: `pytest` (v2: se añade formalmente, hoy falta
  en `pyproject.toml` y no hay carpeta `tests/`).
- Base de datos: archivo `data/recetas.db`, creado automáticamente al primer
  arranque; `data/` se añade a `.gitignore`.
