/* =========================================================
   KOTASTONE — PREMIUM JAVASCRIPT
   All elements are null-checked so this file works safely
   on both index.html and all inner pages.
   ========================================================= */

(function() {
  'use strict';

  /* ── HELPERS ── */
  const $  = id => document.getElementById(id);
  const $$ = sel => document.querySelectorAll(sel);

  /* ── PRELOADER ── */
  window.addEventListener('load', () => {
    setTimeout(() => {
      const pre = $('preloader');
      if (pre) pre.classList.add('hidden');
    }, 700);
  });

  /* ── SCROLL PROGRESS ── */
  function updateScrollProgress() {
    const el = $('scroll-progress');
    if (!el) return;
    const scrollTop  = window.scrollY;
    const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
    el.style.width   = (docHeight ? (scrollTop / docHeight) * 100 : 0) + '%';
  }

  /* ── BACK TO TOP ── */
  const btt = $('back-to-top');
  if (btt) {
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  /* ── SCROLL HANDLER ── */
  function handleScroll() {
    updateScrollProgress();
    if (btt) btt.classList.toggle('visible', window.scrollY > 400);
    const nav = $('navbar');
    if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
    updateActiveNav();
    observeAOS();
    checkCounters();
  }
  window.addEventListener('scroll', handleScroll, { passive: true });

  /* ── MOBILE DRAWER ── */
  // Inject drawer HTML once
  (function injectMobileUI() {
    // Build nav links from existing desktop nav
    const desktopLinks = $$('.nav-menu a');
    let drawerLinks = '';
    const iconMap = {
      'home': 'fa-home', 'about': 'fa-info-circle', 'variants': 'fa-layer-group',
      'finishes': 'fa-paint-brush', 'applications': 'fa-th-large',
      'gallery': 'fa-images', 'why': 'fa-star', 'specs': 'fa-ruler-combined',
      'dealers': 'fa-map-marker-alt', 'testimonials': 'fa-quote-left',
      'blog': 'fa-newspaper', 'contact': 'fa-envelope'
    };
    desktopLinks.forEach(a => {
      const href = a.getAttribute('href');
      const text = a.textContent.trim();
      const key  = href.replace('#', '').toLowerCase();
      const icon = iconMap[key] || 'fa-chevron-right';
      drawerLinks += `<a href="${href}"><i class="fas ${icon}"></i>${text}</a>`;
    });
    // If no nav links found (inner pages), build minimal set
    if (!drawerLinks) {
      drawerLinks = `<a href="index.html"><i class="fas fa-home"></i>Home</a>
        <a href="index.html#variants"><i class="fas fa-layer-group"></i>Variants</a>
        <a href="index.html#gallery"><i class="fas fa-images"></i>Gallery</a>
        <a href="index.html#contact"><i class="fas fa-envelope"></i>Contact</a>`;
    }

    document.body.insertAdjacentHTML('beforeend', `
      <div class="nav-overlay" id="nav-overlay"></div>
      <nav id="mobile-drawer" aria-label="Mobile navigation">
        <div class="drawer-header">
          <div class="drawer-logo">KOTA<span>STONE</span></div>
          <button class="drawer-close" id="drawer-close" aria-label="Close menu"><i class="fas fa-times"></i></button>
        </div>
        <div class="drawer-nav">${drawerLinks}</div>
        <div class="drawer-footer">
          <a href="index.html#contact" class="drawer-cta"><i class="fas fa-book-open"></i>&nbsp;Get Free Catalogue</a>
          <div class="drawer-theme-row">
            <span>Theme</span>
            <button id="drawer-theme" style="background:none;border:1px solid var(--border);border-radius:20px;padding:6px 14px;cursor:pointer;color:var(--text);font-size:0.85rem;">Toggle</button>
          </div>
        </div>
      </nav>
      <div id="mobile-sticky-cta">
        <a href="tel:+918619459354" class="mcta-call"><i class="fas fa-phone-alt"></i> Call Now</a>
        <a href="../outputs/catalogue.pdf" class="mcta-catalogue"><i class="fas fa-book-open"></i> Get Catalogue</a>
      </div>
    `);

    const drawer  = $('mobile-drawer');
    const overlay = $('nav-overlay');
    const drawerClose = $('drawer-close');
    const hamburger   = $('hamburger');

    function openDrawer() {
      drawer.classList.add('open');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      if (hamburger) {
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      }
    }
    function closeDrawer() {
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = '';
      if (hamburger) {
        hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    }

    if (hamburger) hamburger.addEventListener('click', openDrawer);
    if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
    if (overlay) overlay.addEventListener('click', closeDrawer);
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeDrawer));

    // Drawer theme toggle mirrors main theme toggle
    const dTheme = $('drawer-theme');
    if (dTheme) {
      dTheme.addEventListener('click', () => {
        const mainTheme = $('theme-toggle');
        if (mainTheme) mainTheme.click();
      });
    }
  })();

  /* ── ACTIVE NAV ── */
  function updateActiveNav() {
    const sections = $$('section[id]');
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 120) current = sec.id;
    });
    $$('.nav-menu a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  }

  /* ── SMOOTH SCROLL FOR ANCHOR LINKS ── */
  $$('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── DARK MODE ── */
  const themeBtn = $('theme-toggle');
  const root     = document.documentElement;
  const saved    = localStorage.getItem('ks-theme') || 'light';
  root.setAttribute('data-theme', saved);
  if (themeBtn) {
    themeBtn.innerHTML = saved === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    themeBtn.addEventListener('click', () => {
      const isDark = root.getAttribute('data-theme') === 'dark';
      const next   = isDark ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('ks-theme', next);
      themeBtn.innerHTML = next === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
  }

  /* ── HERO SLIDER (index.html only) ── */
  const slides       = $$('.hero-slide');
  const dotsContainer = $('heroDots');
  if (slides.length && dotsContainer) {
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
      $$('.hero-dot')[heroIdx].classList.remove('active');
      heroIdx = ((idx % slides.length) + slides.length) % slides.length;
      slides[heroIdx].classList.add('active');
      $$('.hero-dot')[heroIdx].classList.add('active');
      clearInterval(heroTimer);
      heroTimer = setInterval(() => goHero(heroIdx + 1), 5500);
    }
    const heroPrev = $('heroPrev');
    const heroNext = $('heroNext');
    if (heroPrev) heroPrev.addEventListener('click', () => goHero(heroIdx - 1));
    if (heroNext) heroNext.addEventListener('click', () => goHero(heroIdx + 1));
    heroTimer = setInterval(() => goHero(heroIdx + 1), 5500);

    /* Touch swipe support for hero slider on mobile */
    let heroTouchX = 0;
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
      heroSection.addEventListener('touchstart', e => {
        heroTouchX = e.touches[0].clientX;
      }, { passive: true });
      heroSection.addEventListener('touchend', e => {
        const diff = heroTouchX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) {
          diff > 0 ? goHero(heroIdx + 1) : goHero(heroIdx - 1);
        }
      }, { passive: true });
    }
  }

  /* ── AOS (scroll-trigger animations) ── */
  function observeAOS() {
    /* Lower offset on mobile so elements animate sooner when in viewport */
    const offset = window.innerWidth <= 768 ? 20 : 60;
    $$('[data-aos]:not(.aos-in)').forEach(el => {
      if (el.getBoundingClientRect().top < window.innerHeight - offset) {
        el.classList.add('aos-in');
      }
    });
  }
  observeAOS();
  setTimeout(observeAOS, 300);
  /* Extra trigger for mobile — some devices fire scroll late after first render */
  setTimeout(observeAOS, 800);

  /* ── COUNTER ANIMATION (index.html only) ── */
  let countersRan = false;
  function checkCounters() {
    if (countersRan) return;
    const strip = document.querySelector('.stats-strip');
    if (!strip) return;
    if (strip.getBoundingClientRect().top < window.innerHeight) {
      countersRan = true;
      $$('.stat-num').forEach(el => {
        const target   = parseInt(el.dataset.count);
        const duration = 2000;
        const step     = target / (duration / 16);
        let current    = 0;
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = Math.floor(current).toLocaleString();
        }, 16);
      });
    }
  }

  /* ── SPECS TABS (index.html) ── */
  $$('.spec-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      $$('.spec-tab').forEach(t  => t.classList.remove('active'));
      $$('.spec-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = $('tab-' + tab.dataset.tab);
      if (panel) panel.classList.add('active');
    });
  });

  /* ── GALLERY FILTER (index.html only) ── */
  const filterBtns = $$('.filter-btn');
  const gItems     = $$('.g-item');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;
      gItems.forEach(item => item.classList.toggle('hidden', f !== 'all' && item.dataset.cat !== f));
    });
  });

  /* ── LIGHTBOX (index.html only) ── */
  const lb = $('lightbox');
  if (lb && gItems.length) {
    const lbImg     = $('lb-img');
    const lbCaption = $('lb-caption');
    let lbImages    = [];
    let lbIndex     = 0;

    gItems.forEach(item => {
      item.addEventListener('click', () => {
        lbImages = Array.from($$('.g-item:not(.hidden)'));
        lbIndex  = lbImages.indexOf(item);
        openLb();
      });
    });
    function openLb() {
      const item = lbImages[lbIndex];
      if (!item) return;
      lbImg.src = item.querySelector('img').src;
      if (lbCaption) lbCaption.textContent = item.querySelector('.g-overlay span')?.textContent || '';
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeLb() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    const lbClose = $('lb-close');
    const lbPrev  = $('lb-prev');
    const lbNext  = $('lb-next');
    if (lbClose) lbClose.addEventListener('click', closeLb);
    lb.addEventListener('click', e => { if (e.target === lb) closeLb(); });
    if (lbPrev) lbPrev.addEventListener('click', () => { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; openLb(); });
    if (lbNext) lbNext.addEventListener('click', () => { lbIndex = (lbIndex + 1) % lbImages.length; openLb(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'ArrowLeft')  { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; openLb(); }
      if (e.key === 'ArrowRight') { lbIndex = (lbIndex + 1) % lbImages.length; openLb(); }
    });

    /* Touch swipe for lightbox on mobile */
    let lbTouchX = 0;
    lb.addEventListener('touchstart', e => { lbTouchX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => {
      const diff = lbTouchX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) {
        if (diff > 0) { lbIndex = (lbIndex + 1) % lbImages.length; }
        else          { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; }
        openLb();
      }
    });
  }

  /* ── TESTIMONIAL SLIDER (index.html only) ── */
  const track = $('testiTrack');
  if (track) {
    const cards    = Array.from(track.querySelectorAll('.testi-card'));
    const dotsWrap = $('testiDots');
    let tIdx       = 0;
    let autoTimer;

    /* Compute how many cards are visible based on container width */
    function getPerSlide() {
      const w = track.parentElement.offsetWidth;
      if (w < 580) return 1;
      if (w < 900) return 2;
      return 3;
    }

    /* Get the step distance = one card width + one gap */
    function getStepPx() {
      if (!cards.length) return 0;
      const cardW = cards[0].getBoundingClientRect().width;
      // gap is 24px as set in CSS
      return cardW + 24;
    }

    /* Total "pages" of cards */
    function getPages() {
      return Math.max(1, cards.length - getPerSlide() + 1);
    }

    /* Build navigation dots */
    function buildDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      const pages = getPages();
      for (let i = 0; i < pages; i++) {
        const d = document.createElement('div');
        d.className = 'testi-dot' + (i === 0 ? ' active' : '');
        d.addEventListener('click', () => goTo(i));
        dotsWrap.appendChild(d);
      }
    }

    /* Slide to index idx (clamped) */
    function goTo(idx) {
      const pages = getPages();
      tIdx = Math.max(0, Math.min(idx, pages - 1));
      const step = getStepPx();
      track.style.transform = `translateX(-${tIdx * step}px)`;
      if (dotsWrap) {
        dotsWrap.querySelectorAll('.testi-dot').forEach((d, i) =>
          d.classList.toggle('active', i === tIdx)
        );
      }
    }

    /* Next / Prev with wrapping */
    function next() { goTo(tIdx + 1 >= getPages() ? 0 : tIdx + 1); }
    function prev() { goTo(tIdx - 1 < 0 ? getPages() - 1 : tIdx - 1); }

    /* Auto-play */
    function startAuto() {
      clearInterval(autoTimer);
      autoTimer = setInterval(next, 5500);
    }

    /* Recalculate on resize */
    function setup() {
      tIdx = 0;
      track.style.transform = 'translateX(0)';
      buildDots();
      startAuto();
    }

    /* Initialise after fonts/images settle */
    setTimeout(setup, 100);
    window.addEventListener('resize', () => { setup(); });

    /* Arrow buttons */
    const testiPrev = $('testiPrev');
    const testiNext = $('testiNext');
    if (testiPrev) testiPrev.addEventListener('click', () => { prev(); startAuto(); });
    if (testiNext) testiNext.addEventListener('click', () => { next(); startAuto(); });

    /* Pause on hover */
    track.parentElement.addEventListener('mouseenter', () => clearInterval(autoTimer));
    track.parentElement.addEventListener('mouseleave', startAuto);

    /* Touch / swipe support */
    let touchStartX = 0;
    track.addEventListener('touchstart', e => {
      touchStartX = e.touches[0].clientX;
      /* Pause auto-play while user is touching */
      clearInterval(autoTimer);
    }, { passive: true });
    track.addEventListener('touchend', e => {
      const diff = touchStartX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) { diff > 0 ? next() : prev(); }
      /* Resume auto-play after touch */
      startAuto();
    });
  }

  /* ── DEALER SEARCH (index.html only) ── */
  const dealerSearchBtn = $('dealerSearchBtn');
  if (dealerSearchBtn) {
    const dealerInput = $('dealerSearch');
    function runDealerSearch() {
      const q = dealerInput ? dealerInput.value.toLowerCase().trim() : '';
      $$('.dealer-item').forEach(item => {
        item.style.display = q && !item.textContent.toLowerCase().includes(q) ? 'none' : '';
      });
    }
    dealerSearchBtn.addEventListener('click', runDealerSearch);
    if ($('dealerSearch')) {
      /* Use both keyup and keydown for compatibility with mobile IME keyboards */
      $('dealerSearch').addEventListener('keyup', e => { if (e.key === 'Enter') runDealerSearch(); });
      $('dealerSearch').addEventListener('keydown', e => { if (e.key === 'Enter') runDealerSearch(); });
    }
  }

  /* ── CONTACT FORM (index.html only) ── */
  const contactForm = $('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      // Basic validation
      let valid = true;
      this.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
          field.style.borderColor = '#e74c3c';
          valid = false;
        } else {
          field.style.borderColor = '';
        }
      });
      if (!valid) return;

      const btn = this.querySelector('.btn-submit');
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending…';
      setTimeout(() => {
        btn.disabled  = false;
        btn.innerHTML = 'Send Message <i class="fas fa-paper-plane"></i>';
        const success = $('formSuccess');
        if (success) {
          success.classList.add('show');
          setTimeout(() => success.classList.remove('show'), 6000);
        }
        this.reset();
        this.querySelectorAll('input, textarea').forEach(f => f.style.borderColor = '');
      }, 1800);
    });
  }

  /* ── NEWSLETTER (footer — works on ALL pages) ── */
  function initNewsletterForms() {
    $$('.newsletter-form').forEach(form => {
      const input = form.querySelector('input[type="email"]');
      const btn   = form.querySelector('button');
      if (!input || !btn) return;

      btn.addEventListener('click', () => handleNewsletter(input, btn, form));
      input.addEventListener('keyup', e => {
        if (e.key === 'Enter') handleNewsletter(input, btn, form);
      });
    });
  }

  function handleNewsletter(input, btn, form) {
    const email = input.value.trim();

    // Reset state
    input.style.borderColor = '';
    removeToast(form);

    // Validate email
    if (!email) {
      input.style.borderColor = '#e74c3c';
      input.focus();
      showToast(form, 'Please enter your email address.', 'error');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      input.style.borderColor = '#e74c3c';
      input.focus();
      showToast(form, 'Please enter a valid email address.', 'error');
      return;
    }

    // Sending state
    const origHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    // Simulate API call
    setTimeout(() => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-check"></i>';
      btn.style.background = '#27ae60';
      input.value = '';
      input.style.borderColor = '#27ae60';
      showToast(form, '✓ You\'re subscribed! Thank you.', 'success');

      // Reset button after 3s
      setTimeout(() => {
        btn.innerHTML = origHtml;
        btn.style.background = '';
        input.style.borderColor = '';
        removeToast(form);
      }, 4000);
    }, 1200);
  }

  function showToast(form, msg, type) {
    removeToast(form);
    const toast = document.createElement('div');
    toast.className = 'nl-toast nl-toast--' + type;
    toast.textContent = msg;
    form.parentElement.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('nl-toast--visible'));
  }

  function removeToast(form) {
    const existing = form.parentElement.querySelector('.nl-toast');
    if (existing) existing.remove();
  }

  initNewsletterForms();

  /* ── PARALLAX ON HERO (desktop only for performance) ── */
  if (window.innerWidth > 768) {
    window.addEventListener('scroll', () => {
      const hero = document.querySelector('.hero-content');
      if (hero) hero.style.transform = `translateY(${window.scrollY * 0.3}px)`;
    }, { passive: true });
  }

  /* ── VARIANT CARDS: mobile touch-to-show overlay ── */
  /* On touch devices, hover doesn't fire, so we toggle an 'active' class on tap
     to reveal the overlay. Desktop hover still works via CSS. */
  if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
    $$('.variant-card').forEach(card => {
      card.addEventListener('touchstart', function() {
        /* Close all other open cards first */
        $$('.variant-card.touch-active').forEach(c => {
          if (c !== this) c.classList.remove('touch-active');
        });
        this.classList.toggle('touch-active');
      }, { passive: true });
    });
  }

})();
