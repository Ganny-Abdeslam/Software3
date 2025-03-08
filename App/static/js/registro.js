// Función para activar o desactivar el botón dependiendo del checkbox
function toggleSubmitButton() {
    const checkbox = document.getElementById("check");
    const submitButton = document.getElementById("envio");
    submitButton.disabled = !checkbox.checked;
}

// Validación del formulario
function validate() {
    const v1 = document.getElementById("name");
    const v2 = document.getElementById("rut");
    const v3 = document.getElementById("profesion");
    const v4 = document.getElementById("password");
    const v5 = document.getElementById("fecha");
    const v6 = document.getElementById("email");

    let flag1 = true, flag2 = true, flag3 = true, flag4 = true, flag5 = true, flag6 = true;

    // Validar nombre
    if (v1.value === "") {
        v1.style.borderColor = "red";
        flag1 = false;
    } else {
        v1.style.borderColor = "green";
        flag1 = true;
    }

    // Validar rut
    if (v2.value === "") {
        v2.style.borderColor = "red";
        flag2 = false;
    } else {
        v2.style.borderColor = "green";
        flag2 = true;
    }

    // Validar profesión
    if (v3.value === "") {
        v3.style.borderColor = "red";
        flag3 = false;
    } else {
        v3.style.borderColor = "green";
        flag3 = true;
    }

    // Validar cargo
    if (v4.value === "") {
        v4.style.borderColor = "red";
        flag4 = false;
    } else {
        v4.style.borderColor = "green";
        flag4 = true;
    }

    // Validar jornada
    if (v5.value === "") {
        v5.style.borderColor = "red";
        flag5 = false;
    } else {
        v5.style.borderColor = "green";
        flag5 = true;
    }

    // Validar sueldo
    if (v6.value === "") {
        v6.style.borderColor = "red";
        flag6 = false;
    } else {
        v6.style.borderColor = "green";
        flag6 = true;
    }

    // Retorna true solo si todas las validaciones son correctas
    return flag1 && flag2 && flag3 && flag4 && flag5 && flag6;
}

// Manejar la presentación del formulario
document.querySelector("form").onsubmit = function(event) {
    event.preventDefault();  // Evita el envío del formulario si las validaciones no pasan
    if (validate()) {
        // Si todo es válido, permitir el envío del formulario
        this.submit();
    } else {
        alert("Por favor, complete todos los campos obligatorios.");
    }
};

// Escuchar cambios en el checkbox de términos y condiciones
document.getElementById("check").addEventListener("change", toggleSubmitButton);

// Desactivar el botón de enviar inicialmente
toggleSubmitButton();
