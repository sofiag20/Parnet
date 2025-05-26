function iniciarCarrusel() {
    let indexSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');

    if (!slides.length) return;

    function mostrarSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        indexSlide = (n + slides.length) % slides.length;
        slides[indexSlide].classList.add('active');
    }

    function moverSlide(n) {
        mostrarSlide(indexSlide + n);
    }

    if (prevBtn && nextBtn) {
        prevBtn.onclick = () => moverSlide(-1);
        nextBtn.onclick = () => moverSlide(1);
    }

    setInterval(() => moverSlide(1), 5000);
    mostrarSlide(indexSlide);
}
