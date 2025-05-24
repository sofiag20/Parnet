let indexSlide = 0;
const slides = document.querySelectorAll('.carousel-slide');

function mostrarSlide(n) {
    slides.forEach(slide => slide.classList.remove('active'));
    indexSlide = (n + slides.length) % slides.length;
    slides[indexSlide].classList.add('active');
}

function moverSlide(n) {
    mostrarSlide(indexSlide + n);
}

// Avance automático cada 5 segundos
setInterval(() => moverSlide(1), 5000);

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    mostrarSlide(indexSlide);
});
