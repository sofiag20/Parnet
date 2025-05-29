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

// Delegación: escucha submits en #contenido
document.getElementById("contenido").addEventListener("submit", e => {
    const form = e.target;

  // Crear producto
    if (form.matches('#form-agregar-producto')) {
        e.preventDefault();
        fetch(form.action, {
            method: "POST",
            body: new FormData(form)
        })
        .then(() => cargarContenido("productos_admin2"))
        .catch(() => alert("Error de red al crear"));
    }

    // Editar producto
    else if (form.matches('form[action^="/admin/producto/editar"]')) {
        e.preventDefault();
        fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            redirect: 'follow'
        })
        .then(() => cargarContenido("productos_admin2"))
        .catch(() => alert("Error de red al editar"));
    }

    // Eliminar producto
    else if (form.matches('form[action^="/admin/producto/eliminar"]')) {
        e.preventDefault();
            fetch(form.action, {
            method: "POST",
            body: new FormData(form)
        })
        .then(() => cargarContenido("productos_admin2"))
        .catch(() => alert("Error de red al eliminar"));
    }
});

