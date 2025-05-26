document.addEventListener("DOMContentLoaded", () => {
    const contenido = document.getElementById("contenido");
    const observer = new MutationObserver(() => {
        const form = document.getElementById("formLogin");
        if (!form) return;

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            fetch("/login", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    cargarContenido("admin");
                } else {
                    document.getElementById("error-msg").innerText = data.message;
                }
            })
            .catch(err => {
                console.error("❌ Error de red:", err);
            });
        });
    });

    observer.observe(contenido, { childList: true, subtree: true });
});
