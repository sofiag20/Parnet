document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
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
            if (data.rol === "admin") {
                window.location.href = "/admin/dashboard";
            } else {
                cargarContenido("principal");
            }
            } else {
            document.getElementById("error-msg").innerText = data.message;
            }
        })
        .catch(err => {
            document.getElementById("error-msg").innerText = "Error de red.";
            console.error(err);
        });
    });
});
