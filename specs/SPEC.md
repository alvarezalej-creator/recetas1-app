# Especificación — Gestor de Recetas de Cocina

## 1. Visión general
Aplicación de línea de comandos (CLI) interactiva, escrita en Python, para
gestionar un recetario personal: crear, consultar, editar, eliminar y buscar
recetas. Los datos se persisten en una base de datos **SQLite** local.

- Interfaz: CLI interactiva (menús numerados, `input()`/`print()`).
- Persistencia: SQLite (archivo `data/recetas.db`).
- Arquitectura: **MVC** (Modelo / Vista / Controlador) en carpetas separadas.
- Gestor de entorno y dependencias: **uv**.
- Alcance v1: CRUD completo + búsqueda.

## 2. Funcionalidades (v1)

| # | Funcionalidad | Descripción |
|---|---|---|
| 1 | Añadir receta | Captura nombre, descripción, categoría, tiempo de preparación, porciones, ingredientes (lista) y pasos (lista ordenada). |
| 2 | Listar recetas | Vista resumida: id, nombre, categoría, tiempo de preparación. |
| 3 | Ver detalle de receta | Muestra receta completa: ingredientes con cantidad/unidad y pasos ordenados. |
| 4 | Editar receta | Permite modificar cualquier campo, incluidos ingredientes y pasos. |
| 5 | Eliminar receta | Solicita confirmación antes de borrar (borra también ingredientes/pasos asociados). |
| 6 | Buscar recetas | Por nombre (coincidencia parcial), por ingrediente, o por categoría. |
| 7 | Gestionar categorías | Listar categorías existentes y crearlas al vuelo al añadir/editar una receta. |
| 8 | Salir | Cierra la aplicación de forma segura. |

Fuera de alcance en v1 (posibles extensiones futuras): favoritos, lista de la
compra, imágenes, importar/exportar, multiusuario.

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
0. Salir
```

- **Añadir receta**: formulario guiado paso a paso (nombre → categoría →
  descripción → tiempo → porciones → ingredientes en bucle → pasos en bucle).
- **Listar recetas**: tabla simple en texto con id/nombre/categoría/tiempo.
- **Ver receta**: pide un id, muestra la ficha completa.
- **Buscar recetas**: submenú (por nombre / por ingrediente / por categoría),
  reutiliza la vista de listado para mostrar resultados.
- **Editar receta**: pide id, muestra valores actuales, permite dejar vacío
  para mantener el valor, permite regenerar ingredientes/pasos.
- **Eliminar receta**: pide id, muestra ficha, pide confirmación (s/n).
- **Gestionar categorías**: listar categorías y su número de recetas; crear
  nueva categoría.

## 5. Validaciones clave
- El nombre de la receta es obligatorio y no vacío.
- Al añadir/editar, si la categoría no existe se ofrece crearla.
- `prep_time_minutes` y `servings` deben ser enteros positivos si se informan.
- Una receta debe tener al menos 1 ingrediente y 1 paso para guardarse.
- IDs inexistentes en ver/editar/eliminar → mensaje de error controlado, sin
  crash.

## 6. Arquitectura MVC (estructura de carpetas)

```
recetas1-app/
├── pyproject.toml
├── README.md
├── specs/
│   ├── SPEC.md
│   └── PLAN.md
├── src/
│   └── recetas/
│       ├── __init__.py
│       ├── main.py                 # punto de entrada, wiring, loop principal
│       ├── models/
│       │   ├── __init__.py
│       │   ├── database.py         # conexión SQLite + creación de esquema
│       │   ├── recipe.py           # dataclasses Recipe/Ingredient/Step + acceso a datos
│       │   └── category.py         # dataclass Category + acceso a datos
│       ├── views/
│       │   ├── __init__.py
│       │   ├── menu_view.py        # menús y captura de opciones
│       │   ├── recipe_view.py      # formularios y renderizado de recetas
│       │   └── messages.py         # mensajes de éxito/error/info reutilizables
│       └── controllers/
│           ├── __init__.py
│           ├── recipe_controller.py
│           └── category_controller.py
└── tests/
    ├── test_models.py
    └── test_controllers.py
```

- **Modelo**: acceso a datos (SQLite) y estructuras (`dataclass`). No conoce
  la CLI.
- **Vista**: solo entrada/salida por terminal (prompts, formateo). No conoce
  SQL.
- **Controlador**: orquesta el flujo, valida y conecta vista con modelo.

## 7. Entorno y dependencias
- Gestión con **uv**: `uv init`, `uv add`, `uv run`.
- Dependencias runtime: solo librería estándar (`sqlite3`, `dataclasses`,
  `datetime`) — sin dependencias externas necesarias para v1.
- Dependencias de desarrollo: `pytest` (tests).
- Base de datos: archivo `data/recetas.db`, creado automáticamente al primer
  arranque; `data/` se añade a `.gitignore`.
