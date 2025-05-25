// Cargar citas al iniciar
window.onload = cargarCitas;

// Carga todas las citas del usuario autenticado
async function cargarCitas() {
  try {
    const res = await fetch("/mis_citas");
    const citas = await res.json();
    const container = document.getElementById("citas-container");
    container.innerHTML = "";

    if (citas.length === 0) {
      container.innerHTML = "<p>No tienes citas activas.</p>";
      return;
    }

    citas.forEach(cita => {
      const div = document.createElement("div");
      div.className = "card mb-3";
      div.innerHTML = `
        <div class="card-body">
          <h5 class="card-title">${cita.paciente}</h5>
          <p class="card-text">
            <strong>Fecha:</strong> ${cita.fecha_hora} <br>
            <strong>Motivo:</strong> ${cita.motivo} <br>
            <strong>Estado:</strong> ${cita.estado} <br>
            <strong>Sitio:</strong> ${cita.sitio || "N/A"} <br>
          </p>
          <button class="btn btn-primary btn-sm" onclick="editarCita('${cita._id.$oid}')">✏️ Editar</button>
          <button class="btn btn-success btn-sm" onclick="atenderCita('${cita._id.$oid}')">🩺 Atendido</button>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    console.error("Error al cargar citas:", error);
  }
}

// Editar cita
async function editarCita(citaId) {
  const nuevaFecha = prompt("Nueva fecha (YYYY-MM-DD HH:MM):");
  const nuevoMotivo = prompt("Nuevo motivo:");
  const nuevoEstado = prompt("Nuevo estado (A = activa, C = cancelada, atendido):");

  if (!nuevaFecha || !nuevoMotivo || !nuevoEstado) {
    alert("Todos los campos son obligatorios.");
    return;
  }

  const res = await fetch(`/actualizar_cita/${citaId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fecha_hora: nuevaFecha.trim(),
      motivo: nuevoMotivo.trim(),
      estado: nuevoEstado.trim().toLowerCase()
    })
  });

  const data = await res.json();
  alert(data.mensaje || data.error);
  cargarCitas();
}

// Marcar como atendido
async function atenderCita(citaId) {
  if (!confirm("¿Deseas marcar esta cita como atendida?")) return;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
    const res = await fetch(`/atender_cita/${citaId}`, {
      method: "PUT",
      "X-CSRFToken": csrfToken
    });

    const contentType = res.headers.get("content-type") || "";

    if (!res.ok) {
      const errorText = await res.text();
      console.error("❌ Error HTTP:", res.status, errorText);
      alert(`Error al atender cita: ${res.status}`);
      return;
    }

    if (contentType.includes("application/json")) {
      const data = await res.json();
      alert(data.mensaje || data.error);
    } else {
      const text = await res.text();
      console.warn("⚠️ Respuesta no JSON:", text);
      alert("La cita fue marcada, pero el servidor no devolvió un JSON.");
    }

    cargarCitas();

  } catch (error) {
    console.error("❌ Error al atender cita:", error);
    alert("Error inesperado al atender la cita.");
  }
}