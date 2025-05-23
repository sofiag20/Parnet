// Rotador de noticias automático (noticias.js)
document.addEventListener("DOMContentLoaded", () => {
    const noticias = window.noticiasData || [];

    let index = 0;

    function mostrarSiguienteNoticia() {
        if (noticias.length === 0) return;

        index = (index + 1) % noticias.length;

        const contenedor = document.getElementById("noticia-rotativa");
        contenedor.innerHTML = `
            <p><strong>${noticias[index].titulo}</strong><br>
            ${noticias[index].nota} <a href="#">[Leer más]</a></p>
        `;
    }

    setInterval(mostrarSiguienteNoticia, 5000);
});
