from typing import Optional

from controllers.category_controller import CategoryController
from models.category import CategoryModel
from models.recipe import Recipe, RecipeModel
from views import menu_view


class RecipeController:
    """Flujo de altas, consultas, búsqueda, edición y borrado de recetas."""

    def __init__(
        self,
        recipe_model: RecipeModel,
        category_model: CategoryModel,
        category_controller: CategoryController,
    ) -> None:
        self.recipe_model = recipe_model
        self.category_model = category_model
        self.category_controller = category_controller

    # --- Añadir -----------------------------------------------------

    def add_recipe(self) -> None:
        print("\n--- Añadir receta ---")
        name = menu_view.prompt("Nombre: ")
        if not name:
            menu_view.print_message("El nombre es obligatorio. Operación cancelada.")
            return
        category_id = self.category_controller.resolve_category_id()
        description = menu_view.prompt("Descripción (opcional): ") or None
        prep_time = menu_view.prompt_int("Tiempo de preparación en minutos (opcional): ", allow_empty=True)
        servings = menu_view.prompt_int("Porciones (opcional): ", allow_empty=True)
        ingredients = menu_view.prompt_ingredients()
        steps = menu_view.prompt_steps()

        recipe = self.recipe_model.create(
            name=name,
            description=description,
            category_id=category_id,
            prep_time_minutes=prep_time,
            servings=servings,
            ingredients=ingredients,
            steps=steps,
        )
        menu_view.print_message(f"Receta '{recipe.name}' creada (id {recipe.id}).")

    # --- Listar / ver -------------------------------------------------

    def list_recipes(self) -> None:
        recipes = self.recipe_model.list_all()
        menu_view.print_recipes_table(recipes)

    def view_recipe(self) -> None:
        recipe_id = menu_view.prompt_int("Id de la receta: ")
        recipe = self._get_existing(recipe_id)
        if recipe is not None:
            menu_view.print_recipe_detail(recipe)

    # --- Buscar ---------------------------------------------------------

    def search_recipes(self) -> None:
        while True:
            menu_view.print_search_menu()
            choice = menu_view.prompt("Elige una opción: ")
            if choice == "1":
                query = menu_view.prompt("Nombre a buscar: ")
                menu_view.print_recipes_table(self.recipe_model.search_by_name(query))
            elif choice == "2":
                query = menu_view.prompt("Ingrediente a buscar: ")
                menu_view.print_recipes_table(self.recipe_model.search_by_ingredient(query))
            elif choice == "3":
                self._search_by_category()
            elif choice == "0":
                return
            else:
                menu_view.print_message("Opción no válida.")

    def _search_by_category(self) -> None:
        categories = self.category_model.list_all()
        if not categories:
            menu_view.print_message("No hay categorías registradas todavía.")
            return
        for category in categories:
            print(f"  {category.id}. {category.name}")
        category_id = menu_view.prompt_int("Id de categoría: ")
        if category_id is None:
            return
        menu_view.print_recipes_table(self.recipe_model.search_by_category(category_id))

    # --- Editar -----------------------------------------------------

    def edit_recipe(self) -> None:
        recipe_id = menu_view.prompt_int("Id de la receta a editar: ")
        recipe = self._get_existing(recipe_id)
        if recipe is None:
            return
        menu_view.print_recipe_detail(recipe)
        print("\nDeja un campo vacío para mantener el valor actual.")

        name = menu_view.prompt(f"Nombre [{recipe.name}]: ") or recipe.name
        description = menu_view.prompt(
            f"Descripción [{recipe.description or '-'}]: "
        ) or recipe.description
        prep_time = menu_view.prompt_int(
            f"Tiempo de preparación [{recipe.prep_time_minutes or '-'}]: ", allow_empty=True
        )
        if prep_time is None:
            prep_time = recipe.prep_time_minutes
        servings = menu_view.prompt_int(f"Porciones [{recipe.servings or '-'}]: ", allow_empty=True)
        if servings is None:
            servings = recipe.servings

        category_id: Optional[int] = recipe.category_id
        if menu_view.prompt_confirm("¿Cambiar categoría? (s/n): "):
            category_id = self.category_controller.resolve_category_id()

        ingredients = recipe.ingredients
        if menu_view.prompt_confirm("¿Reemplazar ingredientes? (s/n): "):
            ingredients = menu_view.prompt_ingredients()

        steps = recipe.steps
        if menu_view.prompt_confirm("¿Reemplazar pasos? (s/n): "):
            steps = menu_view.prompt_steps()

        self.recipe_model.update(
            recipe_id=recipe.id,
            name=name,
            description=description,
            category_id=category_id,
            prep_time_minutes=prep_time,
            servings=servings,
            ingredients=ingredients,
            steps=steps,
        )
        menu_view.print_message("Receta actualizada.")

    # --- Eliminar ---------------------------------------------------

    def delete_recipe(self) -> None:
        recipe_id = menu_view.prompt_int("Id de la receta a eliminar: ")
        recipe = self._get_existing(recipe_id)
        if recipe is None:
            return
        menu_view.print_recipe_detail(recipe)
        if menu_view.prompt_confirm("¿Confirmas que quieres eliminarla? (s/n): "):
            self.recipe_model.delete(recipe.id)
            menu_view.print_message("Receta eliminada.")
        else:
            menu_view.print_message("Operación cancelada.")

    # --- Utilidades ---------------------------------------------------

    def _get_existing(self, recipe_id: Optional[int]) -> Optional[Recipe]:
        if recipe_id is None:
            return None
        recipe = self.recipe_model.get_by_id(recipe_id)
        if recipe is None:
            menu_view.print_message(f"No existe ninguna receta con id {recipe_id}.")
        return recipe
