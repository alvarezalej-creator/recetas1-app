from typing import Optional

from models.category import CategoryModel
from views import menu_view


class CategoryController:
    """Flujo de gestión de categorías."""

    def __init__(self, category_model: CategoryModel) -> None:
        self.category_model = category_model

    def run(self) -> None:
        while True:
            menu_view.print_category_menu()
            choice = menu_view.prompt("Elige una opción: ")
            if choice == "1":
                self._list_categories()
            elif choice == "2":
                self._create_category()
            elif choice == "0":
                return
            else:
                menu_view.print_message("Opción no válida.")

    def _list_categories(self) -> None:
        categories = self.category_model.list_all()
        rows = [(c, self.category_model.count_recipes(c.id)) for c in categories]
        menu_view.print_categories_with_counts(rows)

    def _create_category(self) -> None:
        name = menu_view.prompt("Nombre de la categoría: ")
        if not name:
            menu_view.print_message("El nombre no puede estar vacío.")
            return
        if self.category_model.get_by_name(name) is not None:
            menu_view.print_message("Ya existe una categoría con ese nombre.")
            return
        category = self.category_model.create(name)
        menu_view.print_message(f"Categoría '{category.name}' creada (id {category.id}).")

    def resolve_category_id(self) -> Optional[int]:
        """Pide un nombre de categoría; la crea si no existe. Vacío = sin categoría."""
        name = menu_view.prompt("Categoría (vacío = sin categoría): ")
        if not name:
            return None
        existing = self.category_model.get_by_name(name)
        if existing is not None:
            return existing.id
        if menu_view.prompt_confirm(f"La categoría '{name}' no existe. ¿Crearla? (s/n): "):
            return self.category_model.create(name).id
        return None
