document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    
    // Sticky Header Scroll Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });


    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));

    // WhatsApp Widget Logic
    const waButton = document.getElementById('wa-button');
    const waPopup = document.getElementById('wa-popup');
    const waClose = document.getElementById('wa-close');

    if (waButton && waPopup && waClose) {
        waButton.addEventListener('click', () => {
            waPopup.classList.toggle('active');
        });

        waClose.addEventListener('click', () => {
            waPopup.classList.remove('active');
        });
    }
});
