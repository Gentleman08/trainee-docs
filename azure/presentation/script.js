document.addEventListener('DOMContentLoaded', () => {
  const slides = document.querySelectorAll('.slide');
  const counter = document.querySelector('.slide-counter');
  const progress = document.querySelector('.progress-bar');
  let current = 0;

  function showSlide(n) {
    if (n < 0 || n >= slides.length) return;
    slides[current].classList.remove('active');
    current = n;
    slides[current].classList.add('active');
    counter.textContent = `${current + 1} / ${slides.length}`;
    progress.style.width = `${((current + 1) / slides.length) * 100}%`;
  }

  document.getElementById('prev').addEventListener('click', () => showSlide(current - 1));
  document.getElementById('next').addEventListener('click', () => showSlide(current + 1));

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); showSlide(current + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); showSlide(current - 1); }
    if (e.key === 'Home') { e.preventDefault(); showSlide(0); }
    if (e.key === 'End') { e.preventDefault(); showSlide(slides.length - 1); }
  });

  // Touch support
  let touchStartX = 0;
  document.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].screenX; });
  document.addEventListener('touchend', e => {
    const diff = touchStartX - e.changedTouches[0].screenX;
    if (Math.abs(diff) > 50) { diff > 0 ? showSlide(current + 1) : showSlide(current - 1); }
  });

  showSlide(0);
});
