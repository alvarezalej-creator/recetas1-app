from typing import Optional

from models.category import Category
from models.recipe import Ingredient, Recipe, Step


def print_main_menu() -> None:
    print("\n=== Gestor de Recetas ===")
    print("1. Añadir receta")
    print("2. Listar recetas")
    print("3. Ver receta")
    print("4. Buscar recetas")
    print("5. Editar receta")
    print("6. Eliminar receta")
    print("7. Gestionar categorías")
    print("0. Salir")


def print_search_menu() -> None:
    print("\n--- Buscar recetas ---")
    print("1. Por nombre")
    print("2. Por ingrediente")
    print("3. Por categoría")
    print("0. Volver")


def print_category_menu() -> None:
    print("\n--- Gestionar categorías ---")
    print("1. Listar categorías")
    print("2. Crear categoría")
    print("0. Volver")


def prompt(text: str) -> str:
    return input(text).strip()


def prompt_int(text: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        raw = input(text).strip()
        if not raw:
            if allow_empty:
                return None
            print("Este campo es obligatorio.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Debe ser un número entero.")
            continue
        if value <= 0:
            print("Debe ser un número entero positivo.")
            continue
        return value


def prompt_confirm(text: str) -> bool:
    return input(text).strip().lower() in ("s", "si", "sí")


def print_message(message: str) -> None:
    print(message)


def print_recipes_table(recipes: list[Recipe]) -> None:
    if not recipes:
        print("No hay recetas para mostrar.")
        return
    print(f"{'ID':<4} {'Nombre':<30} {'Categoría':<20} {'Tiempo (min)':<12}")
    print("-" * 68)
    for recipe in recipes:
        category = recipe.category_name or "-"
        prep_time = str(recipe.prep_time_minutes) if recipe.prep_time_minutes else "-"
        print(f"{recipe.id:<4} {recipe.name:<30} {category:<20} {prep_time:<12}")


def print_recipe_detail(recipe: Recipe) -> None:
    print(f"\n=== {recipe.name} (id {recipe.id}) ===")
    print(f"Categoría: {recipe.category_name or '-'}")
    print(f"Descripción: {recipe.description or '-'}")
    print(f"Tiempo de preparación: {recipe.prep_time_minutes or '-'} minutos")
    print(f"Porciones: {recipe.servings or '-'}")
    print("\nIngredientes:")
    if not recipe.ingredients:
        print("  (sin ingredientes)")
    for ingredient in recipe.ingredients:
        quantity = f"{ingredient.quantity} " if ingredient.quantity is not None else ""
        unit = f"{ingredient.unit} " if ingredient.unit else ""
        print(f"  - {quantity}{unit}{ingredient.name}")
    print("\nPasos:")
    if not recipe.steps:
        print("  (sin pasos)")
    for step in sorted(recipe.steps, key=lambda s: s.order_index):
        print(f"  {step.order_index}. {step.description}")


def print_categories_with_counts(categories: list[tuple[Category, int]]) -> None:
    if not categories:
        print("No hay categorías todavía.")
        return
    print(f"{'ID':<4} {'Nombre':<25} {'Recetas':<8}")
    print("-" * 37)
    for category, count in categories:
        print(f"{category.id:<4} {category.name:<25} {count:<8}")


def prompt_ingredients() -> list[Ingredient]:
    print("Ingredientes (deja el nombre vacío para terminar, al menos 1):")
    ingredients: list[Ingredient] = []
    while True:
        name = prompt(f"  Ingrediente #{len(ingredients) + 1} - nombre: ")
        if not name:
            if ingredients:
                break
            print("Debes añadir al menos un ingrediente.")
            continue
        quantity = prompt("    cantidad (opcional, ej. 2 o 1/2): ") or None
        unit = prompt("    unidad (opcional): ") or None
        ingredients.append(Ingredient(name=name, quantity=quantity, unit=unit))
    return ingredients


def prompt_steps() -> list[Step]:
    print("Pasos (deja la descripción vacía para terminar, al menos 1):")
    steps: list[Step] = []
    while True:
        description = prompt(f"  Paso #{len(steps) + 1}: ")
        if not description:
            if steps:
                break
            print("Debes añadir al menos un paso.")
            continue
        steps.append(Step(order_index=len(steps) + 1, description=description))
    return steps
