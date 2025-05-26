document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();

    const form = document.getElementById("formAgregar");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch("/admin/producto/crear", {
        method: "POST",
        body: formData
        })
        .then(res => res.json())
        .then(data => {
        if (data.success) {
            form.reset();
            cargarProductos();
        }
        });
    });
});

function cargarProductos() {
    fetch("/api/productos")
        .then(res => res.json())
        .then(data => {
        const tbody = document.querySelector("#tablaProductos tbody");
        tbody.innerHTML = "";

        data.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <td>${p.nombre}</td>
            <td>${p.descripcion}</td>
            <td>${p.precio}</td>
            <td>${p.estatus}</td>
            <td>
                <button onclick="eliminarProducto(${p.id})">Eliminar</button>
            </td>
            `;
            tbody.appendChild(tr);
        });
        });
}

function eliminarProducto(id) {
    fetch(`/admin/producto/eliminar/${id}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
        if (data.success) cargarProductos();
        });
}
