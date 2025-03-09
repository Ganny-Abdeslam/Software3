document.addEventListener("DOMContentLoaded", function () {
    cargarBodegas();
    cargarArticulos();
});

document.getElementById("formBodega").addEventListener("submit", async function (event) {
    event.preventDefault();

    let nombreBodega = document.getElementById("nombreBodega").value.trim();
    if (!nombreBodega) {
        alert("El nombre de la bodega es obligatorio.");
        return;
    }

    let csrfToken = document.querySelector('input[name="csrf_token"]').value;  // 🔥 Obtener CSRF token

    let payload = JSON.stringify({ nombre: nombreBodega });

    try {
        let response = await fetch("/crear_bodega", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-CSRFToken": csrfToken  // 🔥 Incluir token CSRF en los headers
            },
            body: payload
        });

        let data = await response.json();
        if (response.ok) {
            alert(data.mensaje);
            document.getElementById("formBodega").reset();
        } else {
            alert("Error: " + (data.error || "No se pudo crear la bodega"));
        }
    } catch (error) {
        console.error("❌ Error al crear bodega:", error);
        alert("Hubo un problema con la solicitud.");
    }
});


// Cargar bodegas
async function cargarBodegas() {
    try {
        let response = await fetch("/listar_bodegas");
        let data = await response.json();

        let selectBodega = document.getElementById("selectBodega");
        selectBodega.innerHTML = `<option selected disabled>Seleccione una bodega</option>`;

        data.bodegas.forEach(bodega => {
            let option = document.createElement("option");
            option.value = bodega._id;
            option.textContent = bodega.nombre;
            selectBodega.appendChild(option);
        });

        selectBodega.addEventListener("change", () => cargarInventario(selectBodega.value));
    } catch (error) {
        console.error("Error al cargar bodegas:", error);
    }
}

// Cargar artículos
async function cargarArticulos() {
    try {
        let response = await fetch("/listar_articulos");
        let data = await response.json();

        let selectArticulo = document.getElementById("selectArticulo");
        selectArticulo.innerHTML = `<option selected disabled>Seleccione un artículo</option>`;

        data.articulos.forEach(articulo => {
            let option = document.createElement("option");
            option.value = articulo._id;
            option.textContent = articulo.nombre;
            selectArticulo.appendChild(option);
        });
    } catch (error) {
        console.error("Error al cargar artículos:", error);
    }
}

document.getElementById("formArticulo").addEventListener("submit", async function (event) {
    event.preventDefault();

    let bodegaId = document.getElementById("selectBodega").value;
    let articuloId = document.getElementById("selectArticulo").value;
    let cantidad = document.getElementById("cantidad").value;
    let csrfToken = document.querySelector("input[name='csrf_token']").value;  // 🔥 Obtener CSRF

    if (!bodegaId || !articuloId || cantidad <= 0) {
        alert("Debe seleccionar una bodega y un artículo válido.");
        return;
    }

    try {
        let response = await fetch("/agregar_articulo_bodega", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken  // Enviar CSRF en el encabezado
            },
            body: JSON.stringify({ bodegaId, articuloId, cantidad })
        });

        let data = await response.json();
        alert(data.mensaje);
        cargarInventario(bodegaId);
    } catch (error) {
        console.error("Error al agregar artículo:", error);
    }
});

async function cargarInventario(bodegaId) {
    try {
        let response = await fetch(`/inventario_bodega/${bodegaId}`);
        let data = await response.json();
        let tbody = document.getElementById("tablaInventario");
        tbody.innerHTML = "";

        data.articulos.forEach(articulo => {
            let row = `<tr><td>${articulo.nombre}</td><td>${articulo.cantidad}</td></tr>`;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error("Error al cargar inventario:", error);
    }
}

document.getElementById("selectBodega").addEventListener("change", async function () {
    let bodegaId = this.value;
    if (!bodegaId) return;

    try {
        let response = await fetch(`/obtener_inventario/${bodegaId}`);
        let data = await response.json();

        console.log("📦 Inventario recibido:", data.articulos); // Debugging

        if (response.ok) {
            mostrarInventario(data.articulos); 
        } else {
            alert("❌ Error al obtener inventario: " + (data.error || "Desconocido"));
        }
    } catch (error) {
        console.error("❌ Error al obtener inventario:", error);
        alert("Error al cargar el inventario.");
    }
});

function mostrarInventario(inventario) {
    let tabla = document.querySelector("#tabla-inventario tbody");

    if (!tabla) {
        console.error("❌ Error: No se encontró la tabla de inventario en el HTML.");
        return;
    }

    tabla.innerHTML = ""; // Limpiar la tabla antes de actualizar

    if (!inventario || inventario.length === 0) {
        tabla.innerHTML = `<tr><td colspan="2" class="text-center">No hay artículos en esta bodega</td></tr>`;
        return;
    }

    inventario.forEach(item => {
        let fila = document.createElement("tr");
        fila.innerHTML = `
            <td>${item.articulo}</td>  <!-- Ahora muestra directamente el nombre -->
            <td>${item.cantidad}</td>
        `;
        tabla.appendChild(fila);
    });
}

