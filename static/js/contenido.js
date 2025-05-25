function cargarContenido(ruta) {
    fetch(ruta)
        .then(response => response.text())
        .then(html => {
        document.getElementById("contenido").innerHTML = html;

        // 🔁 Reinicia el carrusel después de cargar
        if (ruta.includes("principal")) {
            iniciarCarrusel();
        }
        })
        .catch(error => console.error("Error al cargar contenido:", error));
}
