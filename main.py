import typer

from controllers.category_controller import CategoryController
from controllers.recipe_controller import RecipeController
from models.category import CategoryModel
from models.database import Database
from models.recipe import RecipeModel
from views import menu_view

app = typer.Typer(add_completion=False)


def run_menu(db_path: str = "data/recetas.db") -> None:
    """Ejecuta el bucle principal del menú interactivo."""
    database = Database(db_path)
    category_model = CategoryModel(database)
    recipe_model = RecipeModel(database)
    category_controller = CategoryController(category_model)
    recipe_controller = RecipeController(recipe_model, category_model, category_controller)

    while True:
        menu_view.print_main_menu()
        choice = menu_view.prompt("Elige una opción: ")

        if choice == "1":
            recipe_controller.add_recipe()
        elif choice == "2":
            recipe_controller.list_recipes()
        elif choice == "3":
            recipe_controller.view_recipe()
        elif choice == "4":
            recipe_controller.search_recipes()
        elif choice == "5":
            recipe_controller.edit_recipe()
        elif choice == "6":
            recipe_controller.delete_recipe()
        elif choice == "7":
            category_controller.run()
        elif choice == "0":
            menu_view.print_message("¡Hasta luego!")
            return
        else:
            menu_view.print_message("Opción no válida.")


@app.command()
def main(db_path: str = typer.Option("data/recetas.db", help="Ruta al archivo SQLite.")) -> None:
    """Inicia el Gestor de Recetas de Cocina."""
    run_menu(db_path)


if __name__ == "__main__":
    app()
