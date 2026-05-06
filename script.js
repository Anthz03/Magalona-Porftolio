(() => {
    'use strict';

    const yearEl = document.getElementById('year');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            const isOpen = mobileMenu.classList.toggle('hidden') === false;
            menuBtn.setAttribute('aria-expanded', String(isOpen));
        });

        mobileMenu.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                menuBtn.setAttribute('aria-expanded', 'false');
            });
        });
    }

    const sectionsToReveal = document.querySelectorAll('main section, footer');
    sectionsToReveal.forEach((el) => el.classList.add('reveal'));

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
        );

        sectionsToReveal.forEach((el) => observer.observe(el));
    } else {
        sectionsToReveal.forEach((el) => el.classList.add('is-visible'));
    }

    const typewriterEl = document.getElementById('typewriter');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (typewriterEl && !reduceMotion) {
        const greetings = ['Hello', '안녕', '你好', 'こんにちは', 'Kamusta'];
        const typeSpeed = 110;
        const deleteSpeed = 55;
        const pauseFull = 1600;
        const pauseEmpty = 350;

        let wordIndex = 0;
        let charIndex = greetings[0].length;
        let deleting = true;
        typewriterEl.textContent = greetings[0];

        const tick = () => {
            const current = greetings[wordIndex];

            if (!deleting) {
                charIndex += 1;
                typewriterEl.textContent = current.slice(0, charIndex);
                if (charIndex === current.length) {
                    deleting = true;
                    setTimeout(tick, pauseFull);
                    return;
                }
                setTimeout(tick, typeSpeed);
            } else {
                charIndex -= 1;
                typewriterEl.textContent = current.slice(0, charIndex);
                if (charIndex === 0) {
                    deleting = false;
                    wordIndex = (wordIndex + 1) % greetings.length;
                    setTimeout(tick, pauseEmpty);
                    return;
                }
                setTimeout(tick, deleteSpeed);
            }
        };

        setTimeout(tick, 1800);
    }

    const form = document.getElementById('contactForm');
    const status = document.getElementById('formStatus');

    if (form && status) {
        form.addEventListener('submit', (event) => {
            event.preventDefault();

            const data = new FormData(form);
            const name = String(data.get('name') || '').trim();
            const email = String(data.get('email') || '').trim();
            const message = String(data.get('message') || '').trim();

            if (!name || !email || !message) {
                status.textContent = 'Please fill in every field.';
                status.style.color = '#222222';
                return;
            }

            const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            if (!emailValid) {
                status.textContent = 'That email looks off — mind double-checking?';
                status.style.color = '#222222';
                return;
            }

            status.textContent = 'Thanks — message sent. I\'ll be in touch.';
            status.style.color = '#7B7B7B';
            form.reset();
        });
    }
})();
