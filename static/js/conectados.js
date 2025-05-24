const socket = io();

socket.on('actualizar_conectados', function (numero) {
    const span = document.getElementById("onlineCount");
    if (span) {
        span.textContent = numero;
    }
});

