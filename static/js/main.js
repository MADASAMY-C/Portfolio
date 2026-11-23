document.addEventListener('DOMContentLoaded', () => {
    // ═════════════════════════  INITIALIZATION  ═════════════════════════
    try {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true,
                offset: 100
            });
        }
    } catch (e) {
        console.log("AOS error:", e);
    }

    function hideLoader() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 250);
        }
    }

    // ═════════════════════════  LOADER  ═════════════════════════
    setTimeout(() => {
        hideLoader();
        initTyping(); // Start typing animation after loader
        animateCounters(); // Start counters
    }, 700);

    // ═════════════════════════  CUSTOM CURSOR  ═════════════════════════
    const cursorDot = document.getElementById('cursorDot');
    const cursorRing = document.getElementById('cursorRing');
    
    if (window.innerWidth > 768) {
        window.addEventListener('mousemove', (e) => {
            cursorDot.style.left = e.clientX + 'px';
            cursorDot.style.top = e.clientY + 'px';
            
            // Smoother ring follow
            setTimeout(() => {
                cursorRing.style.left = e.clientX + 'px';
                cursorRing.style.top = e.clientY + 'px';
            }, 50);
        });

        document.querySelectorAll('a, button, .project-card, .contact-card').forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursorRing.style.width = '60px';
                cursorRing.style.height = '60px';
                cursorRing.style.borderColor = 'var(--accent-primary)';
            });
            el.addEventListener('mouseleave', () => {
                cursorRing.style.width = '40px';
                cursorRing.style.height = '40px';
                cursorRing.style.borderColor = 'var(--accent-secondary)';
            });
        });
    } else {
        cursorDot.style.display = 'none';
        cursorRing.style.display = 'none';
    }

    // ═════════════════════════  NAVBAR & MOBILE MENU  ═════════════════════════
    const navbar = document.getElementById('navbar');
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    const navItems = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Active link highlighting
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href').includes(current)) {
                item.classList.add('active');
            }
        });
    });

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    // ═════════════════════════  TYPING ANIMATION  ═════════════════════════
    const roles = ["Data Analyst", "Software Engineer", "AI/ML Engineer"];
    let roleIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingElement = document.getElementById('typingText');

    function initTyping() {
        const currentRole = roles[roleIndex];
        
        if (isDeleting) {
            typingElement.textContent = currentRole.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typingElement.textContent = currentRole.substring(0, charIndex + 1);
            charIndex++;
        }

        let typeSpeed = isDeleting ? 50 : 100;

        if (!isDeleting && charIndex === currentRole.length) {
            typeSpeed = 2000; // Pause at end
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            roleIndex = (roleIndex + 1) % roles.length;
            typeSpeed = 500; // Pause before next word
        }

        setTimeout(initTyping, typeSpeed);
    }

    // ═════════════════════════  DSA COUNTERS  ═════════════════════════
    function animateCounters() {
        const counters = document.querySelectorAll('.dsa-count');
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const duration = 2000;
            const step = target / (duration / 16); // 60fps
            
            let current = 0;
            const updateCounter = () => {
                current += step;
                if (current < target) {
                    counter.innerText = Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.innerText = target;
                }
            };
            updateCounter();
        });
    }

    // ═════════════════════════  CANVAS NEURAL NET  ═════════════════════════
    const canvas = document.getElementById('neuralCanvas');
    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];
    
    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 1;
            this.vy = (Math.random() - 0.5) * 1;
            this.radius = Math.random() * 2 + 1;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 240, 255, 0.5)';
            ctx.fill();
        }
    }

    for (let i = 0; i < 25; i++) particles.push(new Particle());

    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${0.2 - dist/120})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
    }

    let lastFrame = 0;
    function animateCanvas(ts) {
        if (document.hidden) {
            requestAnimationFrame(animateCanvas);
            return;
        }
        if (ts - lastFrame < 33) {
            requestAnimationFrame(animateCanvas);
            return;
        }
        lastFrame = ts || 0;
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawLines();
        requestAnimationFrame(animateCanvas);
    }
    requestAnimationFrame(animateCanvas);

    // ═════════════════════════  FETCH DATA FROM API  ═════════════════════════
    async function fetchWithTimeout(url, ms = 10000) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), ms);
        try {
            const res = await fetch(url, { signal: controller.signal });
            clearTimeout(timeout);
            return res;
        } catch (err) {
            clearTimeout(timeout);
            throw err;
        }
    }

    async function fetchData() {
        // Clear loading states immediately
        const grid = document.getElementById('projectsGrid');
        const skillsContainer = document.getElementById('skillsContainer');
        const achievementsGrid = document.getElementById('achievementsGrid');

        async function loadProjects() {
            try {
                const res = await fetchWithTimeout('/api/projects');
                const projects = await res.json();
                renderProjects(projects);
            } catch (e) {
                console.error('Projects error:', e);
                grid.innerHTML = '<p style="color:#ff375f">Failed to load projects.</p>';
            }
        }

        async function loadSkills() {
            try {
                const res = await fetchWithTimeout('/api/skills');
                const skills = await res.json();
                renderSkills(skills);
            } catch (e) {
                console.error('Skills error:', e);
                skillsContainer.innerHTML = '<p style="color:#ff375f">Failed to load skills.</p>';
            }
        }

        async function loadAchievements() {
            try {
                const res = await fetchWithTimeout('/api/achievements');
                const achievements = await res.json();
                renderAchievements(achievements);
            } catch (e) {
                console.error('Achievements error:', e);
                achievementsGrid.innerHTML = '<p style="color:#ff375f">Failed to load achievements.</p>';
            }
        }

        async function loadCodingProfiles() {
            try {
                const res = await fetchWithTimeout('/api/coding-profiles');
                const profiles = await res.json();
                renderCodingProfiles(profiles);
            } catch (e) {
                console.error('Coding profiles error:', e);
                const container = document.getElementById('codingProfilesContainer');
                if (container) container.innerHTML = '<p style="color:#ff375f">Failed to load coding profiles.</p>';
            }
        }

        // Load all independently (no Promise.all blocking)
        await Promise.all([loadProjects(), loadSkills(), loadAchievements(), loadCodingProfiles()]);

        // Initialize filters after projects loaded
        initFilters();
        window.__pageReady = true;
        hideLoader();
    }

    fetchData();

    // ── Render Projects ──
    function renderProjects(projects) {
        const grid = document.getElementById('projectsGrid');
        grid.innerHTML = '';
        
        if (projects.length === 0) {
            grid.innerHTML = '<p>No projects uploaded yet.</p>';
            return;
        }

        projects.forEach((p, index) => {
            const delay = (index % 3) * 100;
            const techBadges = p.tech_stack ? p.tech_stack.split(',').map(t => `<span class="tech-tag">${t.trim()}</span>`).join('') : '';
            
            const links = `
                ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="project-link"><i class="fab fa-github"></i> Code</a>` : ''}
                ${p.live_url ? `<a href="${p.live_url}" target="_blank" class="project-link"><i class="fas fa-external-link-alt"></i> Live</a>` : ''}
            `;

            const imgPath = p.image_path ? `/static/${p.image_path}` : 'https://via.placeholder.com/400x250?text=Project';

            const card = `
                <div class="project-card" data-category="${p.category}" data-aos="fade-up" data-aos-delay="${delay}">
                    <img src="${imgPath}" alt="${p.title}" class="project-img" onerror="this.src='https://via.placeholder.com/400x250?text=No+Image'"/>
                    <div class="project-content">
                        <span class="project-category">${p.category}</span>
                        <h3 class="project-title">${p.title}</h3>
                        <p class="project-desc">${p.description}</p>
                        <div class="project-tech">${techBadges}</div>
                        <div class="project-links">${links}</div>
                    </div>
                </div>
            `;
            grid.innerHTML += card;
        });
    }

    // ── Render Skills ──
    function renderSkills(skills) {
        const container = document.getElementById('skillsContainer');
        container.innerHTML = '';

        if (skills.length === 0) {
            container.innerHTML = '<p>No skills uploaded yet.</p>';
            return;
        }

        // Group by category
        const categories = {};
        skills.forEach(s => {
            if (!categories[s.category]) categories[s.category] = [];
            categories[s.category].push(s);
        });

        let delay = 0;
        for (const [catName, catSkills] of Object.entries(categories)) {
            let itemsHtml = '';
            catSkills.forEach(s => {
                itemsHtml += `
                    <div class="skill-item">
                        <div class="skill-info">
                            <span class="skill-name"><i class="${s.icon_class}"></i> ${s.name}</span>
                            <span class="skill-percent">${s.percentage}%</span>
                        </div>
                        <div class="skill-bar-bg">
                            <div class="skill-bar-fill" style="width: 0%" data-width="${s.percentage}%"></div>
                        </div>
                    </div>
                `;
            });

            const card = `
                <div class="skill-category-card" data-aos="fade-up" data-aos-delay="${delay}">
                    <h3 class="skill-category-title">${catName}</h3>
                    <div class="skill-list">${itemsHtml}</div>
                </div>
            `;
            container.innerHTML += card;
            delay += 100;
        }

        // Animate skill bars on scroll
        const skillBars = document.querySelectorAll('.skill-bar-fill');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    bar.style.width = bar.getAttribute('data-width');
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.5 });

        skillBars.forEach(bar => observer.observe(bar));
    }

    // ── Render Achievements ──
    function renderAchievements(achievements) {
        const grid = document.getElementById('achievementsGrid');
        grid.innerHTML = '';

        if (achievements.length === 0) {
            grid.innerHTML = '<p>No achievements uploaded yet.</p>';
            return;
        }

        achievements.forEach((a, index) => {
            const delay = (index % 3) * 100;
            const dateStr = a.date_earned ? new Date(a.date_earned).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : '';
            const imgPath = a.image_path ? `/static/${a.image_path}` : '';
            
            let btnHtml = '';
            if (imgPath) {
                btnHtml = `<button class="view-cert-btn" onclick="openLightbox('${imgPath}', '${a.title}')"><i class="fas fa-eye"></i> View Certificate</button>`;
            } else if (a.certificate_url) {
                btnHtml = `<a href="${a.certificate_url}" target="_blank" class="view-cert-btn"><i class="fas fa-external-link-alt"></i> Verify</a>`;
            }

            const card = `
                <div class="achievement-card" data-aos="fade-up" data-aos-delay="${delay}">
                    <i class="fas fa-trophy achievement-icon"></i>
                    ${dateStr ? `<div class="achievement-date">${dateStr}</div>` : ''}
                    <h3 class="achievement-title">${a.title}</h3>
                    <p class="achievement-issuer">${a.issuer}</p>
                    <div class="achievement-actions">${btnHtml}</div>
                </div>
            `;
            grid.innerHTML += card;
        });
    }

    // ── Render Coding Profiles ──────────────────────────────────────────────
    function renderCodingProfiles(profiles) {
        const container = document.getElementById('codingProfilesContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (profiles.length === 0) {
            container.innerHTML = '<p>No coding profiles configured.</p>';
            return;
        }

        profiles.forEach((p, index) => {
            const delay = 200 + (index * 100);
            const stats = p.stats_json || {};
            let statsHtml = '';
            
            // Build stats HTML based on available stats
            const statKeys = Object.keys(stats);
            statKeys.forEach((key, statIndex) => {
                const isLast = statIndex === statKeys.length - 1;
                const className = key.toLowerCase();
                statsHtml += `
                    <div class="dsa-stat ${className}">
                        <div class="dsa-count" data-target="${stats[key]}">0</div>
                        <div class="dsa-label">${key.charAt(0).toUpperCase() + key.slice(1)}</div>
                    </div>
                `;
                if (!isLast) {
                    statsHtml += '<div class="dsa-divider"></div>';
                }
            });

            const widget = `
                <div class="dsa-widget" data-aos="fade-up" data-aos-delay="${delay}">
                    <div class="dsa-header">
                        <i class="${p.icon_class}"></i>
                        <span>${p.display_name || p.platform}</span>
                        <a href="${p.profile_url}" target="_blank" class="dsa-link">View Profile →</a>
                    </div>
                    <div class="dsa-stats">
                        ${statsHtml}
                    </div>
                </div>
            `;
            container.innerHTML += widget;
        });

        // Initialize counter animation for new elements
        initCounterAnimations();
    }

    function initCounterAnimations() {
        const counters = document.querySelectorAll('.dsa-count[data-target]');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            if (isNaN(target)) return;
            
            let current = 0;
            const increment = Math.ceil(target / 50);
            const duration = 1500;
            const stepTime = duration / 50;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = current;
            }, stepTime);
        });
    }

    // ═════════════════════════  PROJECT FILTERS  ═════════════════════════
    function initFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        const cards = document.querySelectorAll('.project-card');

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Active state
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Filter logic
                const filter = btn.getAttribute('data-filter');
                cards.forEach(card => {
                    if (filter === 'all' || card.getAttribute('data-category') === filter) {
                        card.style.display = 'block';
                        setTimeout(() => card.style.opacity = '1', 50);
                    } else {
                        card.style.opacity = '0';
                        setTimeout(() => card.style.display = 'none', 300);
                    }
                });
            });
        });
    }

    // ═════════════════════════  LIGHTBOX  ═════════════════════════
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxOverlay = document.getElementById('lightboxOverlay');

    window.openLightbox = function(src, title) {
        lightboxImg.src = src;
        lightboxCaption.innerText = title;
        lightbox.classList.add('active');
    };

    const closeLightbox = () => lightbox.classList.remove('active');
    lightboxClose.addEventListener('click', closeLightbox);
    lightboxOverlay.addEventListener('click', closeLightbox);

    // ═════════════════════════  CONTACT FORM  ═════════════════════════
    const contactForm = document.getElementById('contactForm');
    const sendMsgBtn = document.getElementById('sendMsgBtn');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const originalBtnText = sendMsgBtn.innerHTML;
        sendMsgBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        sendMsgBtn.disabled = true;

        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.success) {
                contactForm.reset();
                showToast(result.message, 'success');
            } else {
                showToast(result.message, 'error');
            }
        } catch (error) {
            showToast('Failed to send message.', 'error');
        } finally {
            sendMsgBtn.innerHTML = originalBtnText;
            sendMsgBtn.disabled = false;
        }
    });

    function showToast(message, type) {
        toastMsg.innerText = message;
        const icon = toast.querySelector('.toast-icon');
        if (type === 'error') {
            icon.className = 'toast-icon fas fa-exclamation-circle';
            icon.style.color = '#ff375f';
            toast.style.borderColor = '#ff375f';
        } else {
            icon.className = 'toast-icon fas fa-check-circle';
            icon.style.color = '#4ade80';
            toast.style.borderColor = '#4ade80';
        }
        
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
});
