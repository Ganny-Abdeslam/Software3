function filterTable() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("cotizacionesTable");
    tr = table.getElementsByTagName("tr");

    for (i = 2; i < tr.length; i++) { // Empieza desde la segunda fila (la primera es el encabezado)
        tr[i].style.display = "none"; // Oculta todas las filas inicialmente
        td = tr[i].getElementsByTagName("td");
        if (td.length > 0) {
            for (var j = 0; j < td.length; j++) { // Revisa todas las celdas de cada fila
                if (td[j]) {
                    txtValue = td[j].textContent || td[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = ""; // Muestra la fila si encuentra coincidencia
                        break;
                    }
                }
            }
        }
    }
}
