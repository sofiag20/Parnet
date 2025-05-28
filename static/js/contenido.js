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

// Delegación: escucha submits en el contenedor donde cargas los fragmentos
document.getElementById("contenido").addEventListener("submit", e => {
    const form = e.target;
    // Sólo interceptamos los formularios de edición
    if (form.matches('form[action^="/admin/producto/editar"]')) {
        e.preventDefault();
        fetch(form.action, {
        method: "POST",
        body: new FormData(form)
        })
        .then(res => res.json())
        .then(data => {
        if (data.success) {
            // Recarga sólo el fragmento de productos
            cargarContenido("productos_admin");
        } else {
            alert("Error al editar: " + data.error);
        }
        })
        .catch(() => alert("Error de red al editar"));
    }
});
