document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("form-articulo");

    if (!form) {
        console.error("Error: No se encontró el formulario con id 'form-articulo'. Verifica el HTML.");
        return;
    }

    async function cargarArticulos() {
        try {
            const response = await fetch("/listar_articulos");

            if (!response.ok) {
                console.error("Error al obtener artículos:", response.statusText);
                return;
            }

            const data = await response.json();
            console.log("Artículos obtenidos:", data);

            const tabla = document.getElementById("articulosTable");
            if (!tabla) {
                console.error("Error: No se encontró la tabla con id 'articulosTable'.");
                return;
            }

            tabla.innerHTML = ""; // Limpiar tabla antes de llenarla

            data.articulos.forEach(articulo => {
                const fila = document.createElement("tr");

                fila.innerHTML = `
                    <td>${articulo.codigo}</td>
                    <td>${articulo.nombre}</td>
                    <td>${articulo.presentaciones.join(", ")}</td>
                    <td>${articulo.categoria}</td>
                    <td>${articulo.lote}</td>
                `;

                tabla.appendChild(fila);
            });

        } catch (error) {
            console.error("Error al obtener artículos:", error);
        }
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const codigo = document.getElementById("codigo").value.trim();
        const nombre = document.getElementById("nombre").value.trim();
        const presentaciones = document.getElementById("presentaciones").value.trim();
        const categoria = document.getElementById("categoria").value;
        const lote = document.getElementById("lote").value.trim();
        const fecha_vencimiento = document.getElementById("fecha_vencimiento").value;
        let csrfToken = document.querySelector('input[name="csrf_token"]').value;  // 🔥 Obtener CSRF token

        if (!codigo || !nombre || !presentaciones || !categoria) {
            alert("Todos los campos son obligatorios.");
            return;
        }

        const articuloData = {
            codigo,
            nombre,
            presentaciones: presentaciones.split(", "),
            categoria,
            lote,
            fecha_vencimiento
        };

        try {
            const response = await fetch("/guardar_articulo", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-CSRFToken": csrfToken// Añadir CSRF si está presente
                },
                body: JSON.stringify(articuloData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error del servidor:", errorText);
                alert("Error al guardar el artículo: " + errorText);
                return;
            }

            const data = await response.json();
            console.log("Respuesta del servidor:", data);

            alert("Artículo guardado con éxito.");
            form.reset();
            cargarArticulos();
        } catch (error) {
            console.error("Error al guardar:", error);
            alert("Hubo un problema al conectar con el servidor.");
        }
    });

    cargarArticulos();
});
