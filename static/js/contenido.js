function cargarContenido(ruta) {
    fetch(`/contenido/${ruta}`)
        .then(res => {
            if (!res.ok) throw new Error("Error al cargar contenido");
            return res.text();
        })
        .then(html => {
            const cont = document.getElementById("contenido");
            if (cont) {
                cont.innerHTML = html;

                // 🔁 Reinicializa carrusel si es principal
                if (ruta === "principal" && typeof iniciarCarrusel === "function") {
                    iniciarCarrusel();  // llama la función de carrusel
                }
            }
        })
        .catch(err => console.error("Error al cargar contenido:", err));
}
