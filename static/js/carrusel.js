function iniciarCarrusel() {
    let indexSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const btnNext = document.querySelector('.carousel-btn.next');
    const btnPrev = document.querySelector('.carousel-btn.prev');

    if (!slides.length) return;

    function mostrarSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        indexSlide = (n + slides.length) % slides.length;
        slides[indexSlide].classList.add('active');
    }

    function moverSlide(n) {
        mostrarSlide(indexSlide + n);
    }

    btnNext?.addEventListener('click', () => moverSlide(1));
    btnPrev?.addEventListener('click', () => moverSlide(-1));
    setInterval(() => moverSlide(1), 5000);
    mostrarSlide(indexSlide);
}
