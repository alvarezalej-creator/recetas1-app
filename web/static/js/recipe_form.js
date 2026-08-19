// Filas dinámicas de ingredientes/pasos en el formulario de receta,
// usando <template> nativo. El mismo código sirve para alta (vacío)
// y edición (prellenado con lo que ya tenga la receta).

function addIngredientRow(values) {
  values = values || { name: "", quantity: "", unit: "" };
  const template = document.getElementById("ingredient-row-template");
  const list = document.getElementById("ingredients-list");
  const clone = template.content.cloneNode(true);
  const row = clone.querySelector(".ingredient-row");
  const [nameInput, quantityInput, unitInput] = row.querySelectorAll("input");
  nameInput.value = values.name || "";
  quantityInput.value = values.quantity || "";
  unitInput.value = values.unit || "";
  row.querySelector(".remove-row").addEventListener("click", () => row.remove());
  list.appendChild(clone);
}

function addStepRow(value) {
  value = value || "";
  const template = document.getElementById("step-row-template");
  const list = document.getElementById("steps-list");
  const clone = template.content.cloneNode(true);
  const row = clone.querySelector(".step-row");
  row.querySelector("textarea").value = value;
  row.querySelector(".remove-row").addEventListener("click", () => row.remove());
  list.appendChild(clone);
}

document.addEventListener("DOMContentLoaded", () => {
  const addIngredientButton = document.getElementById("add-ingredient");
  const addStepButton = document.getElementById("add-step");
  if (!addIngredientButton || !addStepButton) {
    return; // esta página no tiene el formulario de receta
  }

  const initialIngredients = JSON.parse(
    document.getElementById("initial-ingredients").textContent || "[]"
  );
  const initialSteps = JSON.parse(
    document.getElementById("initial-steps").textContent || "[]"
  );

  if (initialIngredients.length === 0) {
    addIngredientRow();
  } else {
    initialIngredients.forEach((ingredient) => addIngredientRow(ingredient));
  }

  if (initialSteps.length === 0) {
    addStepRow();
  } else {
    initialSteps.forEach((step) => addStepRow(step.description));
  }

  addIngredientButton.addEventListener("click", () => addIngredientRow());
  addStepButton.addEventListener("click", () => addStepRow());
});
