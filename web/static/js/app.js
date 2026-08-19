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
