/* =========================================================
   KOTASTONE — PREMIUM JAVASCRIPT
   ========================================================= */

(function() {
  'use strict';

  /* ── PRELOADER ── */
  window.addEventListener('load', () => {
    setTimeout(() => {
      document.getElementById('preloader').classList.add('hidden');
    }, 2400);
  });

  /* ── SCROLL PROGRESS ── */
  function updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight ? (scrollTop / docHeight) * 100 : 0;
    document.getElementById('scroll-progress').style.width = pct + '%';
  }

  /* ── BACK TO TOP ── */
  const btt = document.getElementById('back-to-top');
  function handleScroll() {
    updateScrollProgress();
    btt.classList.toggle('visible', window.scrollY > 400);
    // Navbar scroll
    document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
    // Active nav link
    updateActiveNav();
    // AOS
    observeAOS();
    // Counters
    checkCounters();
  }
  btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  window.addEventListener('scroll', handleScroll, { passive: true });

  /* ── HAMBURGER ── */
  const hamburger = document.getElementById('hamburger');
  const navMenu = document.getElementById('nav-menu');
  hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('open');
    const spans = hamburger.querySelectorAll('span');
    if (navMenu.classList.contains('open')) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });
  navMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('open');
      hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    });
  });

  /* ── ACTIVE NAV ── */
  function updateActiveNav() {
    const sections = document.querySelectorAll('section[id]');
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 120) current = sec.id;
    });
    document.querySelectorAll('.nav-menu a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  }

  /* ── SMOOTH SCROLL FOR NAV LINKS ── */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── DARK MODE ── */
  const themeBtn = document.getElementById('theme-toggle');
  const root = document.documentElement;
  const saved = localStorage.getItem('ks-theme') || 'light';
  root.setAttribute('data-theme', saved);
  themeBtn.innerHTML = saved === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
  themeBtn.addEventListener('click', () => {
    const isDark = root.getAttribute('data-theme') === 'dark';
    const next = isDark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('ks-theme', next);
    themeBtn.innerHTML = next === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
  });

  /* ── HERO SLIDER ── */
  const slides = document.querySelectorAll('.hero-slide');
  const dotsContainer = document.getElementById('heroDots');
  let heroIdx = 0;
  let heroTimer;

  slides.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'hero-dot' + (i === 0 ? ' active' : '');
    dot.addEventListener('click', () => goHero(i));
    dotsContainer.appendChild(dot);
  });

  function goHero(idx) {
    slides[heroIdx].classList.remove('active');
    document.querySelectorAll('.hero-dot')[heroIdx].classList.remove('active');
    heroIdx = (idx + slides.length) % slides.length;
    slides[heroIdx].classList.add('active');
    document.querySelectorAll('.hero-dot')[heroIdx].classList.add('active');
    resetHeroTimer();
  }
  function resetHeroTimer() {
    clearInterval(heroTimer);
    heroTimer = setInterval(() => goHero(heroIdx + 1), 5500);
  }
  document.getElementById('heroPrev').addEventListener('click', () => goHero(heroIdx - 1));
  document.getElementById('heroNext').addEventListener('click', () => goHero(heroIdx + 1));
  resetHeroTimer();

  /* ── AOS (scroll-trigger animations) ── */
  function observeAOS() {
    document.querySelectorAll('[data-aos]:not(.aos-in)').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 80) {
        el.classList.add('aos-in');
      }
    });
  }
  observeAOS(); // run once on load

  /* ── COUNTER ANIMATION ── */
  let countersRan = false;
  function checkCounters() {
    if (countersRan) return;
    const strip = document.querySelector('.stats-strip');
    if (!strip) return;
    const rect = strip.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      countersRan = true;
      document.querySelectorAll('.stat-num').forEach(el => {
        const target = parseInt(el.dataset.count);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = Math.floor(current).toLocaleString();
        }, 16);
      });
    }
  }

  /* ── SPECS TABS ── */
  document.querySelectorAll('.spec-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.spec-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.spec-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
  });

  /* ── GALLERY FILTER ── */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const gItems = document.querySelectorAll('.g-item');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;
      gItems.forEach(item => {
        const match = f === 'all' || item.dataset.cat === f;
        item.classList.toggle('hidden', !match);
      });
    });
  });

  /* ── LIGHTBOX ── */
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lb-img');
  const lbCaption = document.getElementById('lb-caption');
  let lbImages = [];
  let lbIndex = 0;

  gItems.forEach((item, i) => {
    item.addEventListener('click', () => {
      lbImages = Array.from(document.querySelectorAll('.g-item:not(.hidden)'));
      lbIndex = lbImages.indexOf(item);
      openLightbox();
    });
  });

  function openLightbox() {
    const item = lbImages[lbIndex];
    if (!item) return;
    lbImg.src = item.querySelector('img').src;
    lbCaption.textContent = item.querySelector('.g-overlay span')?.textContent || '';
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  document.getElementById('lb-close').addEventListener('click', closeLightbox);
  lb.addEventListener('click', e => { if (e.target === lb) closeLightbox(); });
  document.getElementById('lb-prev').addEventListener('click', () => { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; openLightbox(); });
  document.getElementById('lb-next').addEventListener('click', () => { lbIndex = (lbIndex + 1) % lbImages.length; openLightbox(); });
  document.addEventListener('keydown', e => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; openLightbox(); }
    if (e.key === 'ArrowRight') { lbIndex = (lbIndex + 1) % lbImages.length; openLightbox(); }
  });
  function closeLightbox() { lb.classList.remove('open'); document.body.style.overflow = ''; }

  /* ── TESTIMONIAL SLIDER ── */
  const track = document.getElementById('testiTrack');
  const cards = track.querySelectorAll('.testi-card');
  const dotsWrap = document.getElementById('testiDots');
  let tIdx = 0;
  let perSlide = window.innerWidth < 580 ? 1 : 3;

  function buildTestiDots() {
    dotsWrap.innerHTML = '';
    const pages = Math.ceil(cards.length / perSlide);
    for (let i = 0; i < pages; i++) {
      const d = document.createElement('div');
      d.className = 'testi-dot' + (i === 0 ? ' active' : '');
      d.addEventListener('click', () => goTesti(i));
      dotsWrap.appendChild(d);
    }
  }

  function goTesti(idx) {
    const pages = Math.ceil(cards.length / perSlide);
    tIdx = (idx + pages) % pages;
    const offset = tIdx * (100 / perSlide);
    // Each card takes 1/3 (or 1/1) of track width
    track.style.transform = `translateX(-${tIdx * (100 / perSlide)}%)`;
    // Actually compute per card width
    const cardW = (track.parentElement.offsetWidth - 48) / perSlide;
    track.style.transform = `translateX(-${tIdx * (cardW + 24) * perSlide}px)`;
    dotsWrap.querySelectorAll('.testi-dot').forEach((d, i) => d.classList.toggle('active', i === tIdx));
  }

  // Simpler approach — translate by full slider width per "page"
  function goTesti2(idx) {
    const pages = Math.ceil(cards.length / perSlide);
    tIdx = (idx + pages) % pages;
    const sliderW = track.parentElement.offsetWidth;
    track.style.transform = `translateX(-${tIdx * sliderW}px)`;
    dotsWrap.querySelectorAll('.testi-dot').forEach((d, i) => d.classList.toggle('active', i === tIdx));
  }

  // Use full-width approach — make track children wrap into groups
  // Simplest reliable approach: just shift by card count
  function setupTestiSlider() {
    perSlide = window.innerWidth < 580 ? 1 : 3;
    buildTestiDots();
    // Width of each card is 1/perSlide of container
    cards.forEach(c => { c.style.minWidth = `calc(${100 / perSlide}% - ${perSlide > 1 ? '16px' : '0px'})`; });
    goTesti(0);
  }

  setupTestiSlider();
  window.addEventListener('resize', setupTestiSlider);

  function goTesti(idx) {
    const pages = Math.ceil(cards.length / perSlide);
    tIdx = ((idx % pages) + pages) % pages;
    const cardW = cards[0].offsetWidth + 24;
    track.style.transform = `translateX(-${tIdx * perSlide * cardW}px)`;
    if (dotsWrap) dotsWrap.querySelectorAll('.testi-dot').forEach((d, i) => d.classList.toggle('active', i === tIdx));
  }

  document.getElementById('testiPrev').addEventListener('click', () => goTesti(tIdx - 1));
  document.getElementById('testiNext').addEventListener('click', () => goTesti(tIdx + 1));
  setInterval(() => goTesti(tIdx + 1), 6000);

  /* ── DEALER SEARCH ── */
  document.getElementById('dealerSearchBtn').addEventListener('click', () => {
    const q = document.getElementById('dealerSearch').value.toLowerCase();
    document.querySelectorAll('.dealer-item').forEach(item => {
      item.style.display = q && !item.textContent.toLowerCase().includes(q) ? 'none' : '';
    });
  });
  document.getElementById('dealerSearch').addEventListener('keyup', e => {
    if (e.key === 'Enter') document.getElementById('dealerSearchBtn').click();
  });

  /* ── CONTACT FORM ── */
  document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const btn = this.querySelector('.btn-submit');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending…';
    setTimeout(() => {
      btn.disabled = false;
      btn.innerHTML = 'Send Message <i class="fas fa-paper-plane"></i>';
      document.getElementById('formSuccess').classList.add('show');
      this.reset();
      setTimeout(() => document.getElementById('formSuccess').classList.remove('show'), 6000);
    }, 1800);
  });

  /* ── PARALLAX ON HERO ── */
  window.addEventListener('scroll', () => {
    const hero = document.querySelector('.hero-content');
    if (hero) {
      hero.style.transform = `translateY(${window.scrollY * 0.35}px)`;
    }
  }, { passive: true });

  // Initial AOS trigger
  setTimeout(observeAOS, 200);

})();
