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
            image: 'img/VERIFAI/screen.png',
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
        fbms: {
            title: 'FBMS Kiosk',
            meta: 'De La Salle-College of Saint Benilde · 2026',
            role: 'System Analyst / Developer',
            image: 'img/FBMS/screen.png',
            description: [
                'FBMS Kiosk is an Android-based Feedback Management System designed for Benilde service counters such as the Registrar\'s Office and Library, allowing students and visitors to quickly submit feedback after receiving service.',
                'The kiosk authenticates as a trusted device, dynamically loads administrator-published surveys, and anonymously submits responses while automatically associating each submission with its department and location.'
            ],
            bullets: [
                'Designed a kiosk-based feedback experience requiring no user login or app installation',
                'Implemented trusted device authentication for public-facing Android tablets',
                'Enabled dynamic rendering of administrator-published surveys and different question types',
                'Configured anonymous feedback submission with automatic department and location tracking',
                'Implemented online/offline device status monitoring for staff visibility',
                'Designed the system to reliably collect feedback across multiple Benilde service counters'
            ],
            stack: 'Android · Feedback Management · REST API · Kiosk System',
            linkUrl: 'https://github.com/Anthz03/MOBDEVT-FBMS-Kiosk',
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
            image: 'img/CLICKSHIFT/screen.png',
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
        bms: {
            title: 'Barangay Management System',
            meta: 'Barangay Management System · 2026',
            role: 'System Analyst / Developer',
            image: 'img/BMS/screen.png',

            description: [
                'The Barangay Management System is a centralized web-based platform designed to streamline the management of barangay records, services, and administrative operations.',
                'The system provides modules for resident and household management, document issuance, scheduling, announcements, audit logging, user management, and reporting, with role-based access for Admin and Staff users.'
            ],

            bullets: [
                'Implemented authentication with separate Admin and Staff access levels',
                'Developed resident management with search, registration, editing, deactivation, RBI renewal, and duplicate entry checking',
                'Implemented household management for family heads, members, and household records',
                'Developed document request and issuance workflows with PDF printing and downloading',
                'Implemented calendar-based scheduling with event creation, editing, deletion, and monthly PDF generation',
                'Developed announcements with categories, images, filtering, editing, and soft deletion',
                'Implemented immutable audit logs tracking actors, actions, timestamps, and affected records',
                'Implemented Admin-only user management with role assignment and account activation/deactivation',
                'Developed reports for resident and document data with date-range filtering and PDF/print export',
                'Implemented role-based access control and input sanitization across the system'
            ],

            stack: 'Web Application · Django · Database Management · RBAC',

            linkUrl: 'https://github.com/Anthz03/Barangay-Management-System',
            linkLabel: 'View on GitHub',
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

    const journeyIsMobile = window.matchMedia('(max-width: 767px)').matches;
    if (journeySlider && journeyTrack && journeySection && !reduceMotion && journeyIsMobile) {
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

        // Pins are calculated for a top-down layout. If the browser restores a
        // mid-page scroll position on reload, the pinned Journey section lays
        // out wrong — everything below it shifts by the pin length and Journey
        // appears blank until you scroll to the top and a refresh corrects it.
        // Opt out of scroll restoration so a reload always starts at the top,
        // where pins position correctly. ScrollTrigger resets this to 'auto' on
        // every refresh, so re-assert it after each one (and set it now).
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
            ScrollTrigger.addEventListener('refresh', () => {
                history.scrollRestoration = 'manual';
            });
        }

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
                    initQuote(isDesktop);
                }
            );
        });

        // Late-loading images (Journey photos, project art, Mori) change layout
        // and can mis-place triggers; refresh once everything has loaded.
        // Also: the pinned Journey only lays out correctly from a top-down
        // scroll, so if a reload left the page scrolled mid-document, force it
        // back to the top first (unless deep-linked to an anchor) before the
        // refresh — otherwise Journey renders shifted/blank until you scroll up.
        window.addEventListener('load', () => {
            // If a reload left the page scrolled mid-document, force it back to
            // the top (unless deep-linked to an anchor) before the refresh, so
            // the pinned Journey doesn't render shifted/blank. The refresh below
            // re-asserts manual scroll restoration via the listener above.
            if (!window.location.hash) {
                window.scrollTo(0, 0);
                if (lenis) lenis.scrollTo(0, { immediate: true });
            }
            ScrollTrigger.refresh();
        });
    }

    // Scroll-effect implementations, invoked from the matchMedia callback above.
    function initSectionReveals() {
        const els = document.querySelectorAll('main section');

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

        // The footer is revealed on its own trigger, NOT in the batch above.
        // It sits at the very bottom of the document, so a 'top 88%' start can
        // resolve just past the maximum scroll position and never fire — the
        // footer would stay hidden the first time you reach Contact. 'top
        // bottom' fires the moment it enters the viewport (including during the
        // Contact anchor jump), so it's always reachable.
        const footer = document.querySelector('footer');
        if (footer) {
            gsap.set(footer, { autoAlpha: 0, y: 40 });
            gsap.to(footer, {
                autoAlpha: 1,
                y: 0,
                duration: 0.7,
                ease: 'power2.out',
                scrollTrigger: { trigger: footer, start: 'top bottom', once: true },
            });
        }
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

        // Desktop: pin the section and scrub the belt horizontally with scroll.
        if (isDesktop) {
            const slider = section.querySelector('.journey-slider');
            const track = section.querySelector('.journey-track');
            if (slider && track) {
                const distance = () => Math.max(0, track.scrollWidth - slider.clientWidth);
                gsap.to(track, {
                    x: () => -distance(),
                    ease: 'none',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top top',
                        end: () => '+=' + distance(),
                        pin: true,
                        scrub: 1,
                        anticipatePin: 1,
                        invalidateOnRefresh: true,
                        // Journey sits above Experience/Skills/etc. Refresh this
                        // pin first so its added scroll length is accounted for
                        // when those later sections' triggers compute positions
                        // (otherwise they fire ~1 pin-length too early).
                        refreshPriority: 1,
                    },
                });
            }
        }

        // Heading + intro reveal — scoped to the header div so it doesn't
        // grab the slide caption <p>s inside the belt. (Both branches.)
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
    function initTimeline() {
        const section = document.getElementById('experience');
        const ol = document.querySelector('#experience ol');
        if (!ol) return;
        const items = Array.from(ol.querySelectorAll('li'));
        if (!items.length) return;

        items.forEach((item) => {
            const dot = item.querySelector('span');
            if (dot) dot.classList.add('timeline-dot');
        });

        // Marks the GSAP-driven path so the rest/active dimming in CSS only
        // applies when entries are actually being animated (keeps the
        // reduced-motion / no-JS fallback fully visible).
        ol.classList.add('is-animated');

        // The heading fades/rises in with the section, then scrolls away
        // normally (not pinned, not sticky).
        if (section) {
            const head = section.querySelectorAll(':scope > div p, :scope > div h2');
            if (head.length) {
                gsap.from(head, {
                    autoAlpha: 0,
                    y: 30,
                    duration: 0.6,
                    ease: 'power2.out',
                    stagger: 0.08,
                    scrollTrigger: { trigger: section, start: 'top 75%', once: true },
                });
            }
        }

        // Each entry fades in exactly when the rail line reaches its dot. The
        // line below is drawn so its leading edge tracks the FOCUS viewport line
        // (start 'top FOCUS' → end 'bottom FOCUS' keeps the drawn front pinned
        // there); firing each entry's reveal when its top hits that same line
        // makes the fade-in coincide with the line connecting the dot.
        const FOCUS = '60%';
        items.forEach((item) => {
            gsap.from(item, {
                autoAlpha: 0,
                y: 56,
                duration: 0.8,
                ease: 'power3.out',
                scrollTrigger: { trigger: item, start: 'top ' + FOCUS, once: true },
            });
        });

        // Vertical rail line draws downward; its front stays at the FOCUS line.
        gsap.fromTo(
            ol,
            { '--tl-scale': 0 },
            {
                '--tl-scale': 1,
                ease: 'none',
                scrollTrigger: { trigger: ol, start: 'top ' + FOCUS, end: 'bottom ' + FOCUS, scrub: 1 },
            }
        );

        // Enlarge the dot of the entry nearest the focus line.
        // The entry currently crossing the viewport center is "active" — its
        // dot enlarges/rings and it brightens to full while its neighbours rest
        // dimmed. The center band gives a wide, continuous active window.
        items.forEach((item) => {
            ScrollTrigger.create({
                trigger: item,
                start: 'top center',
                end: 'bottom center',
                onToggle: (self) => item.classList.toggle('is-active', self.isActive),
            });
        });
    }

    // Quote interlude — "Turning Ideas Into Efficient Systems".
    // Desktop: CSS-sticky stage with a scroll-scrubbed word-by-word reveal.
    // Mobile: one-shot sequenced reveal on view-enter (no pin).
    function initQuote(isDesktop) {
        const section = document.getElementById('philosophy');
        if (!section) return;

        const words = Array.from(section.querySelectorAll('.quote-word'));
        const fill = section.querySelector('.quote-progress-fill');
        if (!words.length) return;

        const N = words.length;
        const slot = 1 / N;
        const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

        // Map raw scroll progress (0..1) so all words finish by ~0.85,
        // leaving a hold tail where the full quote stays bright before release.
        const HOLD_TAIL = 0.85;

        function render(rawProgress) {
            const p = clamp(rawProgress / HOLD_TAIL, 0, 1);

            words.forEach((word, i) => {
                // reach: 0 -> 1 as scroll passes this word's slot, then holds.
                const reach = clamp((p - i * slot) / slot, 0, 1);

                // active: triangular peak (1.0) only while this word is current,
                // falling to 0 within +/- one slot of its center.
                const center = (i + 0.5) * slot;
                const active = clamp(1 - Math.abs(p - center) / slot, 0, 1);

                const opacity = 0.2 + reach * 0.45 + active * 0.35;
                const scale = 1 + active * 0.04;
                const glow = active;

                gsap.set(word, {
                    opacity: opacity,
                    scale: scale,
                    textShadow: '0 0 ' + (glow * 18) + 'px rgb(var(--rgb-primary) / ' + (glow * 0.25) + ')',
                });
            });

            if (fill) gsap.set(fill, { width: (rawProgress * 100) + '%' });
        }

        if (isDesktop) {
            // Mute baseline immediately so nothing flashes full-bright.
            render(0);
            ScrollTrigger.create({
                trigger: section,
                start: 'top top',
                end: 'bottom bottom',
                scrub: 1,
                invalidateOnRefresh: true,
                onUpdate: (self) => render(self.progress),
            });
        } else {
            // Mobile: no pin. One-shot sequenced reveal on view-enter.
            gsap.set(words, { opacity: 0.2, scale: 1 });
            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: 'top 75%',
                    toggleActions: 'play none none none',
                },
            });
            tl.to(words, {
                opacity: 0.85,
                duration: 0.4,
                stagger: 0.18,
                ease: 'power2.out',
            });
            if (fill) {
                tl.to(fill, { width: '100%', duration: words.length * 0.18 + 0.4, ease: 'none' }, 0);
            }
        }
    }
})();
