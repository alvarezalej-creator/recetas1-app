// Si la foto de una receta (URL externa) no carga, cae al placeholder 🍳
// en vez de mostrar el ícono de imagen rota del navegador.
function onRecipePhotoError(img) {
  const placeholder = document.createElement("div");
  placeholder.className = img.className + " " + img.className.replace(
    /(recipe-card-photo|recipe-hero-photo)/, "$1-placeholder"
  );
  placeholder.textContent = "🍳";
  placeholder.setAttribute("aria-hidden", "true");
  img.replaceWith(placeholder);
}

// Confirmación antes de enviar cualquier formulario de borrado.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const message = form.dataset.confirm || "¿Confirmás la acción?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
});
