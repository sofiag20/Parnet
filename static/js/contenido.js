function cargarContenido(nombre) {
    fetch(`/contenido/${nombre}`)
        .then(response => response.text())
        .then(html => {
            const contenedor = document.querySelector(".main-content");
            if (contenedor) {
                contenedor.innerHTML = html;
                inicializarCarrusel(); // ✅ después de cargar contenido
            }
        })
    .catch(error => console.error("Error cargando contenido:", error));
}

