function cargarContenido(ruta) {
    fetch(ruta)
        .then(response => response.text())
        .then(html => {
            document.getElementById("contenido").innerHTML = html;
        })
        .catch(error => console.error("Error al cargar contenido:", error));
}
