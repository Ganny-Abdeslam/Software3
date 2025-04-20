document.addEventListener("DOMContentLoaded", async () => {
    const tabla = document.getElementById("tabla-citas");

    try {
        const response = await fetch("/listar_citas");
        if (!response.ok) throw new Error("Error al cargar las citas");

        const citas = await response.json();
        if (!Array.isArray(citas)) throw new Error("Respuesta inválida");

        citas.forEach(cita => {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${cita.paciente || "N/A"}</td>
                <td>${cita.email || "N/A"}</td>
                <td>${formatFecha(cita.fecha_hora)}</td>
                <td>${cita.motivo || "N/A"}</td>
                <td>${cita.profesional || "N/A"}</td>
                <td>${cita.sitio || "N/A"}</td>
                <td>${traducirEstado(cita.estado)}</td>
            `;

            tabla.appendChild(fila);
        });
    } catch (err) {
        console.error("Error al listar citas:", err);
        tabla.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Error al cargar citas.</td></tr>`;
    }
});

function formatFecha(fechaStr) {
    if (!fechaStr) return "N/A";
    const fecha = new Date(fechaStr);
    return isNaN(fecha) ? "Fecha inválida" : fecha.toLocaleString();
}

function traducirEstado(estado) {
    switch (estado) {
        case "A": return "Activa";
        case "I": return "Inactiva";
        case "T": return "Atendida";
        default: return "Desconocido";
    }
}
