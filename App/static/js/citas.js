document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-cita");
    const profesionalSelect = document.getElementById("profesional");

    if (!form) {
        console.error("Formulario no encontrado");
        return;
    }

    // Cargar profesionales en el select
    fetch("/profesionales")
        .then(res => res.json())
        .then(data => {
            data.forEach(prof => {
                const option = document.createElement("option");
                option.value = prof.nombre;
                option.textContent = prof.nombre;
                profesionalSelect.appendChild(option);
            });
        })
        .catch(err => {
            console.error("Error cargando profesionales:", err);
            alert("No se pudieron cargar los profesionales.");
        });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();  // Evita envío tradicional del formulario

        const paciente_id = document.getElementById("paciente_id").value.trim();
        const paciente = document.getElementById("nombre_paciente").value.trim();
        const email = document.getElementById("email").value.trim();
        const fecha_hora = document.getElementById("fecha_hora").value;
        const motivo = document.getElementById("motivo").value.trim();
        const profesional = profesionalSelect.value;
        const sitio = document.getElementById("sitio").value;
        const csrfToken = document.querySelector("input[name='csrf_token']")?.value;

        if (!profesional) {
            alert("Por favor seleccione un profesional.");
            return;
        }

        const cita = {
            paciente_id,
            paciente,
            email,
            fecha_hora,
            motivo,
            profesional,
            sitio
        };

        try {
            const response = await fetch("/guardar_cita", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(csrfToken && { "X-CSRFToken": csrfToken })
                },
                body: JSON.stringify(cita)
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.error || "Error al guardar la cita.");
            alert("Cita guardada correctamente.");
            form.reset();
        } catch (error) {
            console.error("Error al guardar la cita:", error);
            alert("Hubo un error al guardar la cita. Intenta de nuevo.");
        }
    });
});
