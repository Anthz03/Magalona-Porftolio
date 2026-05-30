(() => {
    'use strict';

    const themeToggle = document.getElementById('themeToggle');
    const iconMoon = document.getElementById('iconMoon');
    const iconSun = document.getElementById('iconSun');
    const profileImg = document.getElementById('profileImg');
    const profileImg2 = document.getElementById('profileImg2');
    const moriExperience = document.getElementById('moriExperience');
    const moriContact = document.getElementById('moriContact');

    const syncIcons = () => {
        const isDark = document.documentElement.classList.contains('dark');
        iconMoon?.classList.toggle('hidden', isDark);
        iconSun?.classList.toggle('hidden', !isDark);
        if (profileImg)  profileImg.src  = isDark ? 'img/profile-dark.png'  : 'img/profile.jpg';
        if (profileImg2) profileImg2.src = isDark ? 'img/profile2-dark.png' : 'img/profile-2.jpg';
        if (moriExperience) moriExperience.src = isDark ? 'img/Mori/Mori-3-dark.jpg' : 'img/Mori/Mori-3.jpg';
        if (moriContact)    moriContact.src    = isDark ? 'img/Mori/Mori-2-dark.jpg' : 'img/Mori/Mori-2.jpg';
    };
    syncIcons();

    themeToggle?.addEventListener('click', () => {
        document.documentElement.classList.add('theme-transitioning');
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        syncIcons();
        window.setTimeout(() => document.documentElement.classList.remove('theme-transitioning'), 300);
    });

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

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const sectionsToReveal = document.querySelectorAll('main section, footer');

    // When GSAP scroll motion is active, initSectionReveals() handles these.
    // Otherwise (reduced motion or GSAP unavailable) reveal immediately.
    const gsapActive =
        typeof window.gsap !== 'undefined' &&
        typeof window.ScrollTrigger !== 'undefined' &&
        !reduceMotion;

    if (!gsapActive) {
        sectionsToReveal.forEach((el) => el.classList.add('reveal', 'is-visible'));
    }

    const typewriterEl = document.getElementById('typewriter');

    if (typewriterEl && !reduceMotion) {
        const greetings = ['Hello', '안녕', '你好', 'こんにちは', 'Kumusta'];
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

    const projectsData = {
        verifai: {
            title: 'VerifAI',
            meta: 'HackFest GDG Loyola · March 2026',
            role: 'Lead System Analyst',
            image: 'img/VerifAI.png',
            description: [
                'VerifAI is an AI-powered Google Docs extension that helps researchers and students verify the credibility of their sources in real time, directly inside the document they\'re writing.',
                'Built during HackFest GDG Loyola, the tool surfaces a 100-point credibility score for each citation — cutting research verification time by roughly 40% compared to manual fact-checking workflows.',
            ],
            bullets: [
                'Led system analysis from concept through to delivery',
                'Designed the 100-point credibility scoring model',
                'Authored data flow diagrams, use cases, and the SRS',
                'Coordinated with the dev team on Google Workspace API integration',
            ],
            stack: 'Google Docs Add-on · AI · System Analysis',
            linkUrl: 'https://github.com/abbychiu7/hackfest26',
            linkLabel: 'View on GitHub',
        },
        pathingin: {
            title: 'Pathingin',
            meta: 'UPLB Warframes Web Design Competition · February 16 – 23, 2026',
            role: 'Web Design Contestant',
            image: 'img/PATHINGIN.png',
            description: [
                'Pathingin is an AI-driven, real-time disaster navigation prototype designed for multi-agency emergency response in the Philippines.',
                'Designed during the UPLB Warframes Web Design Competition, the project focused on simplifying complex multi-agency disaster data into clean, navigable interfaces — with motion used purposefully to clarify rather than decorate.',
            ],
            bullets: [
                'Designed UI/UX end-to-end in Figma',
                'Built intuitive flows for end users in high-stress scenarios',
                'Crafted transition animations to clarify multi-agency data',
                'Ranked 10th of 20 competing teams',
            ],
            stack: 'Figma · UI/UX · Prototype',
            linkUrl: 'https://www.figma.com/design/asr2xN8vTSPKvUM7tEcYpv/PatHingin-TEAM-VION?node-id=2010-224&t=5aMrwzpmLliFPtjE-1',
            linkLabel: 'View on Figma',
        },
        unicheck: {
            title: 'UniCheck PH',
            meta: 'DLS-CSB · September – December 2025',
            role: 'Project Lead & System Analyst',
            image: 'img/UniCheck.png',
            description: [
                'UniCheck PH is an AI-powered academic integrity platform built during my second-year systems coursework at De La Salle - College of Saint Benilde.',
                'I led the project end-to-end — authoring the full SRS, modeling the system through DFDs and use cases, and tracking requirements via the RTM. The platform centralizes plagiarism and AI detection so institutions can run academic checks from a single dashboard.',
            ],
            bullets: [
                'Led the team as project lead and system analyst',
                'Authored the SRS and complete system documentation',
                'Designed centralized plagiarism and AI detection workflows',
                'Modeled real-time dashboards and reporting features',
            ],
            stack: 'Systems Analysis · SRS · DFD · RTM',
            linkUrl: 'https://docs.google.com/document/d/1tH4VAXwsYBH9bsY_kx1QUurJaq0kiJfmUIuHY_NfrVQ/edit?usp=sharing',
            linkLabel: 'View document',
        },
        clickshift: {
            title: 'ClickShift',
            meta: 'DLS-CSB · May – August 2025',
            role: 'System Developer',
            image: 'img/ClickShift.png',
            description: [
                'ClickShift is a web-based smart scheduling system that automates shift generation and rotation for organizations managing rotating staff — built to solve the fairness and overlap problems that come with manual scheduling.',
                'I built the platform end-to-end during my first-year systems coursework, focusing on real input formats (CSV/Excel) and the scheduling logic that actually decides who works when.',
            ],
            bullets: [
                'Built the full web-based scheduling system end-to-end',
                'Implemented CSV/Excel parsing for staff data import',
                'Designed conflict validation to eliminate scheduling overlaps',
                'Wrote shift rotation logic that improves fairness over time',
            ],
            stack: 'C# · ASP.NET · SQL',
        },
    };

    const modal = document.getElementById('projectModal');
    const modalBackdrop = document.getElementById('projectModalBackdrop');
    const modalClose = document.getElementById('projectModalClose');
    const modalImage = document.getElementById('projectModalImage');
    const modalImageWrap = document.getElementById('projectModalImageWrap');
    const modalTitle = document.getElementById('projectModalTitle');
    const modalMeta = document.getElementById('projectModalMeta');
    const modalRole = document.getElementById('projectModalRole');
    const modalDescription = document.getElementById('projectModalDescription');
    const modalBullets = document.getElementById('projectModalBullets');
    const modalStack = document.getElementById('projectModalStack');
    const modalLink = document.getElementById('projectModalLink');

    let lastTrigger = null;

    const setText = (el, value) => {
        if (el) el.textContent = value || '';
    };

    const openProjectModal = (key, trigger) => {
        const data = projectsData[key];
        if (!data || !modal) return;

        if (data.image) {
            modalImage.src = data.image;
            modalImage.alt = data.title;
            modalImageWrap.classList.remove('hidden');
        } else {
            modalImage.removeAttribute('src');
            modalImageWrap.classList.add('hidden');
        }

        setText(modalMeta, data.meta);
        setText(modalTitle, data.title);
        setText(modalRole, data.role);
        setText(modalStack, data.stack);

        modalDescription.innerHTML = (data.description || [])
            .map((p) => `<p>${p}</p>`)
            .join('');

        modalBullets.innerHTML = (data.bullets || [])
            .map(
                (b) =>
                    `<li class="flex gap-3"><span class="text-secondary mt-1">·</span><span>${b}</span></li>`
            )
            .join('');

        const linkUrl = data.linkUrl || data.github;
        const linkLabel = data.linkLabel || (data.github ? 'View on GitHub' : 'View project');

        if (linkUrl) {
            modalLink.href = linkUrl;
            modalLink.innerHTML = `${linkLabel} <span aria-hidden="true">↗</span>`;
            modalLink.classList.remove('hidden');
        } else {
            modalLink.classList.add('hidden');
        }

        lastTrigger = trigger || null;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
        requestAnimationFrame(() => modal.classList.add('is-open'));

        modalClose?.focus();
    };

    const closeProjectModal = () => {
        if (!modal) return;
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');

        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }, 250);

        if (lastTrigger && typeof lastTrigger.focus === 'function') {
            lastTrigger.focus();
        }
        lastTrigger = null;
    };

    document.querySelectorAll('[data-project-trigger]').forEach((btn) => {
        btn.addEventListener('click', (event) => {
            event.preventDefault();
            openProjectModal(btn.dataset.projectTrigger, btn);
        });
    });

    modalBackdrop?.addEventListener('click', closeProjectModal);
    modalClose?.addEventListener('click', closeProjectModal);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closeProjectModal();
        }
    });

    // Lifted to IIFE scope so initJourney() can read the marquee handle for
    // scroll-velocity reactivity. Assigned lazily when the marquee first inits.
    let journeyMarqueeAnim = null;
    const journeySlider = document.querySelector('.journey-slider');
    const journeyTrack = document.querySelector('.journey-track');
    const journeySection = document.getElementById('journey');

    if (journeySlider && journeyTrack && journeySection && !reduceMotion) {
        const initMarquee = () => {
            const slides = journeyTrack.querySelectorAll('.journey-slide');
            if (slides.length < 9) return;

            // Pixel distance between slide[0] and its first duplicate (slide[8])
            const halfOffset =
                slides[8].getBoundingClientRect().left -
                slides[0].getBoundingClientRect().left;

            journeyMarqueeAnim = journeyTrack.animate(
                [
                    { transform: 'translateX(0px)' },
                    { transform: `translateX(-${halfOffset}px)` }
                ],
                { duration: 52000, iterations: Infinity, easing: 'linear' }
            );

            journeySlider.addEventListener('mouseenter', () => journeyMarqueeAnim.pause());
            journeySlider.addEventListener('mouseleave', () => journeyMarqueeAnim.play());
        };

        const journeyObserver = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) {
                    initMarquee();
                    journeyObserver.disconnect();
                }
            },
            { threshold: 0.1 }
        );
        journeyObserver.observe(journeySection);
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

    // ---- GSAP scroll system ----
    const hasGsap = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

    if (hasGsap && !reduceMotion) {
        gsap.registerPlugin(ScrollTrigger);
        ScrollTrigger.config({ ignoreMobileResize: true });

        // ---- Lenis smooth scroll (progressive enhancement) ----
        // Drives the real page scroll (no wrapper transform), so the fixed
        // header and ScrollTrigger pinning keep working. Bridged to GSAP.
        const hasLenis = typeof window.Lenis !== 'undefined';
        let lenis = null;
        if (hasLenis) {
            lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
            lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.add((time) => lenis.raf(time * 1000));
            gsap.ticker.lagSmoothing(0);
        }

        // Route in-page anchor links through Lenis so they land under the
        // fixed header. The header is the fixed top nav; read its height live.
        if (lenis) {
            const header = document.querySelector('header');
            document.querySelectorAll('a[href^="#"]').forEach((link) => {
                link.addEventListener('click', (event) => {
                    const id = link.getAttribute('href');
                    if (!id || id === '#') return;
                    const target = document.querySelector(id);
                    if (!target) return;
                    event.preventDefault();
                    const offset = header ? -header.offsetHeight : 0;
                    // Fixed ~1s ease-out jump (quick start, gentle settle) so
                    // near and far links feel equally snappy-but-smooth.
                    lenis.scrollTo(target, {
                        offset,
                        duration: 1,
                        easing: (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
                    });
                });
            });
        }

        gsap.context(() => {
            const mm = gsap.matchMedia();

            mm.add(
                {
                    isDesktop: '(min-width: 768px)',
                    isMobile: '(max-width: 767px)',
                },
                (ctx) => {
                    const { isDesktop } = ctx.conditions;
                    initSectionReveals();
                    initHero(isDesktop);
                    initAboutSkills(isDesktop);
                    initProjects(isDesktop);
                    initMori(isDesktop);
                    initTimeline(isDesktop);
                    initJourney(isDesktop);
                }
            );
        });

        // Late-loading images (Journey photos, project art, Mori) change layout
        // and can mis-place triggers; refresh once everything has loaded.
        window.addEventListener('load', () => ScrollTrigger.refresh());
    }

    // Scroll-effect implementations, invoked from the matchMedia callback above.
    function initSectionReveals() {
        const els = document.querySelectorAll('main section, footer');

        // Set the pre-animation state GSAP tweens FROM *before* the batch is
        // created, so there's no flash of fully-visible content on first paint.
        // GSAP owns this inline state — we deliberately do NOT add the `.reveal`
        // CSS class here (its transition would fight GSAP's writes); `.reveal`
        // is only for the non-GSAP fallback path above.
        gsap.set(els, { autoAlpha: 0, y: 40 });

        ScrollTrigger.batch(els, {
            start: 'top 88%',
            onEnter: (batch) =>
                gsap.to(batch, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.7,
                    ease: 'power2.out',
                    stagger: 0.08,
                    overwrite: true,
                }),
            once: true,
        });
    }
    function initHero(isDesktop) {
        if (!isDesktop) return;
        const hero = document.querySelector('main > section.relative');
        if (!hero) return;

        const portrait = document.getElementById('profileImg');
        const portraitWrap = portrait ? portrait.closest('.group') : null;
        const sideRail = hero.querySelector('div.hidden.md\\:flex');
        const stats = hero.querySelector('.flex.flex-wrap.gap-12');

        // Portrait drifts up slightly slower than the page.
        if (portraitWrap) {
            gsap.to(portraitWrap, {
                yPercent: -22,
                ease: 'none',
                scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 1 },
            });
        }

        // Side rail ("Information Systems / 2026") drifts gently down.
        if (sideRail) {
            gsap.to(sideRail, {
                yPercent: 26,
                ease: 'none',
                scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 1 },
            });
        }

        // Stats row fades/translates out as the hero leaves the viewport.
        if (stats) {
            gsap.to(stats, {
                autoAlpha: 0,
                y: -20,
                ease: 'none',
                scrollTrigger: { trigger: hero, start: 'center top', end: 'bottom top', scrub: 1 },
            });
        }
    }
    function initAboutSkills() {
        // About: heading rises in, then the body paragraphs stagger in.
        const about = document.getElementById('about');
        if (about) {
            const heading = about.querySelector('h2');
            const paras = about.querySelectorAll('p.leading-relaxed');
            if (heading) {
                gsap.from(heading, {
                    autoAlpha: 0,
                    y: 28,
                    duration: 0.7,
                    ease: 'power3.out',
                    scrollTrigger: { trigger: about, start: 'top 78%', once: true },
                });
            }
            if (paras.length) {
                gsap.from(paras, {
                    autoAlpha: 0,
                    y: 18,
                    duration: 0.6,
                    ease: 'power2.out',
                    stagger: 0.1,
                    scrollTrigger: { trigger: about, start: 'top 72%', once: true },
                });
            }
        }

        // Skills: the bordered grid cells assemble in with a subtle scale + rise.
        const skills = document.getElementById('skills');
        if (skills) {
            const cells = skills.querySelectorAll('.grid > .bg-tertiary');
            if (cells.length) {
                gsap.from(cells, {
                    autoAlpha: 0,
                    scale: 0.98,
                    y: 16,
                    duration: 0.5,
                    ease: 'power2.out',
                    stagger: { each: 0.06, from: 'start' },
                    scrollTrigger: { trigger: skills, start: 'top 75%', once: true },
                });
            }
        }
    }

    function initJourney(isDesktop) {
        const section = document.getElementById('journey');
        if (!section) return;

        // 2a. Scroll-velocity reactivity: speed the marquee with scroll velocity.
        // The marquee handle is assigned lazily (on scroll-into-view), so the
        // trigger is created unconditionally and guards inside onUpdate.
        let resetTimer = null;
        ScrollTrigger.create({
            trigger: section,
            start: 'top bottom',
            end: 'bottom top',
            onUpdate: (self) => {
                if (!journeyMarqueeAnim) return;
                const v = self.getVelocity();              // px/sec, signed
                const boost = 1 + Math.min(Math.abs(v) / 1500, 3); // 1..4
                journeyMarqueeAnim.playbackRate = boost;
                clearTimeout(resetTimer);
                resetTimer = setTimeout(() => {
                    if (journeyMarqueeAnim) journeyMarqueeAnim.playbackRate = 1;
                }, 180);
            },
        });

        // 2b. Intra-frame parallax on each slide image (desktop only).
        if (isDesktop) {
            section.querySelectorAll('.journey-slide img').forEach((img) => {
                gsap.fromTo(
                    img,
                    { yPercent: -5 },
                    {
                        yPercent: 5,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: section,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true,
                        },
                    }
                );
            });
        }

        // 2c. Heading + intro reveal — scoped to the header div so it doesn't
        // grab the slide caption <p>s inside the marquee.
        const header = section.querySelector(':scope > div');
        const heads = header ? header.querySelectorAll('h2, p') : [];
        if (heads.length) {
            gsap.from(heads, {
                autoAlpha: 0,
                y: 20,
                duration: 0.6,
                ease: 'power2.out',
                stagger: 0.06,
                scrollTrigger: { trigger: section, start: 'top 80%', once: true },
            });
        }
    }
    function initProjects(isDesktop) {
        const section = document.getElementById('projects');
        if (!section) return;

        // Heading + intro reveal — scoped to the header grid so it doesn't grab
        // the per-card meta/description/stack <p>s in the card grid.
        const header = section.querySelector(':scope > div');
        const intro = header ? header.querySelectorAll('h2, p') : [];
        if (intro.length) {
            gsap.from(intro, {
                autoAlpha: 0,
                y: 20,
                duration: 0.6,
                ease: 'power2.out',
                stagger: 0.06,
                scrollTrigger: { trigger: section, start: 'top 80%', once: true },
            });
        }

        // Cards rise + fade with stagger.
        const cards = section.querySelectorAll('article.group');
        if (cards.length) {
            gsap.from(cards, {
                autoAlpha: 0,
                y: 40,
                duration: 0.7,
                ease: 'power3.out',
                stagger: 0.12,
                scrollTrigger: { trigger: section, start: 'top 72%', once: true },
            });
        }

        // In-frame image parallax (desktop only).
        if (isDesktop) {
            cards.forEach((card) => {
                const img = card.querySelector('img');
                if (!img) return;
                gsap.fromTo(
                    img,
                    { yPercent: -5 },
                    {
                        yPercent: 5,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: card,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true,
                        },
                    }
                );
            });
        }
    }
    function initMori(isDesktop) {
        if (!isDesktop) return; // heavy parallax is desktop-only
        // #moriExperience is intentionally excluded: the Experience section is
        // pinned (initTimeline), so its Mori stays fixed rather than drifting.
        const moris = [
            { el: document.getElementById('moriContact'), section: document.getElementById('contact') },
        ];

        moris.forEach(({ el, section }) => {
            if (!el || !section) return;
            gsap.fromTo(
                el,
                { yPercent: -18 },
                {
                    yPercent: 18,
                    ease: 'none',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top bottom',
                        end: 'bottom top',
                        scrub: 1,
                        invalidateOnRefresh: true,
                    },
                }
            );
        });
    }
    function initTimeline(isDesktop) {
        const ol = document.querySelector('#experience ol');
        if (!ol) return;
        const items = Array.from(ol.querySelectorAll('li'));
        if (!items.length) return;

        // Mobile / reduced-motion / no-GSAP: leave entries in normal vertical
        // flow, fully visible (no pin, no stepper).
        if (!isDesktop) return;

        const section = document.getElementById('experience');
        if (!section) return;

        // Pin the section and reveal entries ONE AT A TIME: the heading and the
        // Mori stay fixed (they live in the pinned section) while each entry
        // crossfades in over a long scroll. `.is-stepper` switches the <ol> to
        // the absolute-stacked layout in CSS; without it the list is the
        // normal fallback.
        ol.classList.add('is-stepper');
        gsap.set(items, { autoAlpha: 0 });
        gsap.set(items[0], { autoAlpha: 1 });
        gsap.set(ol, { '--tl-scale': 0 });

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: section,
                start: 'top top',
                end: () => '+=' + items.length * window.innerHeight * 0.8,
                pin: true,
                scrub: 1,
                anticipatePin: 1,
                invalidateOnRefresh: true,
            },
        });

        // Crossfade between consecutive entries, holding (dwell) on each.
        for (let i = 1; i < items.length; i += 1) {
            tl.to(items[i - 1], { autoAlpha: 0, ease: 'none', duration: 0.4 })
                .to(items[i], { autoAlpha: 1, ease: 'none', duration: 0.4 }, '>-0.15')
                .to({}, { duration: 0.5 });
        }

        // Draw the timeline rail downward across the whole sequence, so the
        // line descends in step with the experiences and the fixed title.
        tl.to(ol, { '--tl-scale': 1, ease: 'none', duration: tl.duration() }, 0);
    }
})();
