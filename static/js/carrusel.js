let indexSlide = 0;
let slides = [];

function mostrarSlide(n) {
    slides.forEach(slide => slide.classList.remove('active'));
    indexSlide = (n + slides.length) % slides.length;
    slides[indexSlide].classList.add('active');
    }

function moverSlide(n) {
    mostrarSlide(indexSlide + n);
}

function inicializarCarrusel() {
    slides = document.querySelectorAll('.carousel-slide');
    if (slides.length > 0) {
        indexSlide = 0;
        mostrarSlide(indexSlide);
        setInterval(() => moverSlide(1), 5000);
    }
}
