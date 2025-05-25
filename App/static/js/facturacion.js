document.addEventListener("DOMContentLoaded", () => {
  initFactura();
});

let inventario = [];
let facturaItems = [];

// Inicialización general
function initFactura() {
  bindFormSubmit();
  bindAgregarClick();
  cargarBodegas();
}

// 1) Cargar todas las bodegas en el <select>
async function cargarBodegas() {
  try {
    const res = await fetch("/listar_bodegas");
    const { bodegas } = await res.json();

    const selectBodega = document.getElementById("selectBodega");
    selectBodega.innerHTML = `<option value="" disabled selected>Seleccione una bodega</option>`;
    bodegas.forEach(b => {
      const opt = document.createElement("option");
      opt.value = b._id;
      opt.textContent = b.nombre;
      selectBodega.appendChild(opt);
    });

    // Cuando cambie la bodega, cargar su inventario
    selectBodega.addEventListener("change", () => cargarInventario(selectBodega.value));
  } catch (err) {
    console.error("Error al cargar bodegas:", err);
  }
}

// 2) Obtener inventario de la bodega seleccionada
async function cargarInventario(bodegaId) {
  try {
    const res = await fetch(`/obtener_inventarioFact/${bodegaId}`);
    const { articulos } = await res.json();

    inventario = articulos.map(a => ({
      articulo_id: a.articulo_id,
      nombre:       a.nombre,
      disponible:   a.cantidad,
      precio:       a.precio
    }));

    poblardeSelectArticulo();
    document.getElementById("inventario-card").style.display = "";
  } catch (err) {
    console.error("Error cargando inventario:", err);
  }
}

// 3) Poblado del <select> de artículos
function poblardeSelectArticulo() {
  const selArt = document.getElementById("selectArticulo");
  selArt.innerHTML = `<option value="" disabled selected>Seleccione un artículo</option>`;

  inventario.forEach(i => {
    const opt = document.createElement("option");
    opt.value = i.articulo_id;
    opt.textContent = `${i.nombre} (disp: ${i.disponible})`;
    opt.dataset.precio = i.precio;
    selArt.appendChild(opt);
  });
}

// 4) Bindear evento de “Agregar Artículo”
function bindAgregarClick() {
  document.getElementById("btnAgregar").addEventListener("click", () => {
    const selArt = document.getElementById("selectArticulo");
    const artId = selArt.value;
    const qtyEl = document.getElementById("inputCantidad");
    let qty = parseInt(qtyEl.value, 10) || 0;

    // Obtener precio desde atributo data
    const precio = parseFloat(selArt.selectedOptions[0].dataset.precio) || 0;
    const item = inventario.find(i => i.articulo_id === artId);
    if (!item || qty < 1) return;

    // No exceder stock
    qty = Math.min(qty, item.disponible);

    // Agregar o actualizar
    const exists = facturaItems.find(i => i.articulo_id === artId);
    if (exists) {
      exists.cantidad = Math.min(exists.cantidad + qty, item.disponible);
    } else {
      facturaItems.push({ ...item, cantidad: qty });
    }

    qtyEl.value = "";
    renderFactura();
  });
}

// 5) Renderizar la tabla de factura y bindear botones de eliminar
function renderFactura() {
  const tbody = document.getElementById("factura-tbody");
  tbody.innerHTML = "";

  if (facturaItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">Agrega artículos para ver el detalle</td></tr>`;
    calcularTotal();
    return;
  }

  facturaItems.forEach(it => {
    const sub = (it.cantidad * it.precio).toFixed(2);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${it.nombre}</td>
      <td>${it.cantidad}</td>
      <td>$${it.precio.toFixed(2)}</td>
      <td>$${sub}</td>
      <td>
        <button class="btn btn-sm btn-danger btn-remove" data-id="${it.articulo_id}">
          X
        </button>
      </td>`;
    tbody.appendChild(tr);
  });

  // Borrar artículo al hacer click
  tbody.querySelectorAll(".btn-remove").forEach(btn => {
    btn.addEventListener("click", () => {
      facturaItems = facturaItems.filter(i => i.articulo_id !== btn.dataset.id);
      renderFactura();
    });
  });

  calcularTotal();
}

// 6) Calcular y mostrar total (consulta + artículos)
function calcularTotal() {
  const costo = parseFloat(document.getElementById("costoConsulta").value) || 0;
  const totalArt = facturaItems.reduce((sum, i) => sum + (i.cantidad * i.precio), 0);
  document.getElementById("totalFactura").textContent = (costo + totalArt).toFixed(2);
}

// 7) Enviar factura al backend y resetear formulario
function bindFormSubmit() {
  document.getElementById("factura-form").addEventListener("submit", async e => {
    e.preventDefault();

    const email  = document.getElementById("emailPaciente").value.trim();
    const costo  = parseFloat(document.getElementById("costoConsulta").value) || 0;
    const bodega = document.getElementById("selectBodega").value;

    if (!email || !bodega || facturaItems.length === 0) {
      return alert("Completa correo, bodega y agrega al menos un artículo.");
    }

    const payload = {
      email,
      bodega_id:       bodega,
      costo_consulta:  costo,
      items:           facturaItems
    };

    const resp = await fetch("/generar_factura", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });

    if (!resp.ok) {
      return alert("Error generando factura: " + resp.status);
    }

    const { mensaje } = await resp.json();
    alert(mensaje);

    // Reset
    facturaItems = [];
    e.target.reset();
    renderFactura();
    document.getElementById("inventario-card").style.display = "none";
  });
}
