document.addEventListener('DOMContentLoaded', function () {
    // Obtener referencias a los dos checkboxes
    const checkbox1 = document.getElementById('flexSwitchCheckDefault');
    const checkbox2 = document.getElementById('flexSwitchCheckChecked');

    // Función para desactivar el otro checkbox al marcar uno
    function toggleCheckbox(event) {
        if (event.target === checkbox1 && checkbox1.checked) {
            checkbox2.checked = false;  // Desactiva el segundo checkbox si el primero está marcado
        } else if (event.target === checkbox2 && checkbox2.checked) {
            checkbox1.checked = false;  // Desactiva el primero si el segundo está marcado
        }
    }

    // Añadir eventos de cambio para escuchar cuando se marquen los checkboxes
    checkbox1.addEventListener('change', toggleCheckbox);
    checkbox2.addEventListener('change', toggleCheckbox);
});
