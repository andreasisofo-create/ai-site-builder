/* ============================================================
   GSAP Universal Animation Engine v2.0
   Auto-injected in every generated site
   Effects: parallax, text-split, typewriter, magnetic, 3D tilt,
   floating, gradient-flow, blur-in, curtain, morphing, glass,
   marquee, counter, stagger, scroll-progress
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  gsap.registerPlugin(ScrollTrigger);

  /* ----------------------------------------------------------
     1. CORE SCROLL ANIMATIONS (data-animate="...")
     ---------------------------------------------------------- */
  var animations = {
    'fade-up':      { y: 60, opacity: 0 },
    'fade-down':    { y: -60, opacity: 0 },
    'fade-left':    { x: -80, opacity: 0 },
    'fade-right':   { x: 80, opacity: 0 },
    'scale-in':     { scale: 0.8, opacity: 0 },
    'scale-up':     { scale: 0.6, opacity: 0, y: 30 },
    'rotate-in':    { rotation: -8, opacity: 0, y: 40 },
    'flip-up':      { rotationX: 90, opacity: 0, transformPerspective: 600 },
    'blur-in':      { filter: 'blur(20px)', opacity: 0, y: 20 },
    'slide-up':     { y: 100, opacity: 0 },
    'reveal-left':  { clipPath: 'inset(0 100% 0 0)', opacity: 0 },
    'reveal-right': { clipPath: 'inset(0 0 0 100%)', opacity: 0 },
    'reveal-up':    { clipPath: 'inset(100% 0 0 0)', opacity: 0 },
    'reveal-down':  { clipPath: 'inset(0 0 100% 0)', opacity: 0 },
    'bounce-in':    { scale: 0.3, opacity: 0 },
    'zoom-out':     { scale: 1.3, opacity: 0 }
  };

  document.querySelectorAll('[data-animate]').forEach(function (el) {
    var type = el.getAttribute('data-animate');
    if (['stagger', 'parallax', 'text-split', 'typewriter', 'float', 'marquee', 'tilt', 'magnetic', 'gradient-flow', 'morph-bg', 'count-up'].indexOf(type) !== -1) return;
    var config = animations[type];
    if (!config) { el.style.opacity = 1; return; }

    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 0.9);
    var easing = el.getAttribute('data-ease') || (type === 'bounce-in' ? 'elastic.out(1,0.5)' : 'power3.out');

    gsap.fromTo(el, Object.assign({}, config), {
      y: 0, x: 0, scale: 1, opacity: 1, rotation: 0, rotationX: 0,
      filter: 'blur(0px)',
      clipPath: 'inset(0 0% 0 0)',
      duration: dur, delay: delay, ease: easing,
      scrollTrigger: { trigger: el, start: 'top 88%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     2. STAGGER ANIMATION (data-animate="stagger")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="stagger"]').forEach(function (container) {
    var items = container.querySelectorAll('.stagger-item');
    if (!items.length) return;
    var effect = container.getAttribute('data-stagger-effect') || 'fade-up';
    var from = { opacity: 0 };
    if (effect === 'fade-up')    Object.assign(from, { y: 50 });
    if (effect === 'scale-in')   Object.assign(from, { scale: 0.7 });
    if (effect === 'blur-in')    Object.assign(from, { filter: 'blur(12px)', y: 20 });
    if (effect === 'slide-left') Object.assign(from, { x: -60 });

    gsap.fromTo(items, from, {
      y: 0, x: 0, scale: 1, opacity: 1, filter: 'blur(0px)',
      duration: 0.7, stagger: { each: 0.12, from: 'start' },
      ease: 'power3.out',
      scrollTrigger: { trigger: container, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     3. PARALLAX SCROLLING (data-animate="parallax")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="parallax"]').forEach(function (el) {
    var speed = parseFloat(el.getAttribute('data-speed') || 0.3);
    var direction = el.getAttribute('data-direction') || 'y';
    var props = {};
    props[direction] = function () { return -ScrollTrigger.maxScroll(window) * speed; };
    gsap.to(el, {
      y: direction === 'y' ? speed * -200 : 0,
      x: direction === 'x' ? speed * -200 : 0,
      ease: 'none',
      scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: 1.5 }
    });
  });

  /* ----------------------------------------------------------
     4. TEXT SPLIT ANIMATION (data-animate="text-split")
     Splits text into chars/words and animates them
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="text-split"]').forEach(function (el) {
    var splitBy = el.getAttribute('data-split') || 'chars';
    var text = el.textContent;
    el.innerHTML = '';
    el.style.opacity = 1;
    var pieces = splitBy === 'words' ? text.split(/\s+/) : text.split('');

    pieces.forEach(function (piece, i) {
      var span = document.createElement('span');
      span.textContent = piece === ' ' || (splitBy === 'words' && i < pieces.length - 1) ? piece + ' ' : piece;
      span.style.display = 'inline-block';
      span.style.opacity = '0';
      if (piece === ' ') span.style.width = '0.3em';
      el.appendChild(span);
    });

    gsap.fromTo(el.children, { y: splitBy === 'words' ? 30 : 15, opacity: 0, rotationX: splitBy === 'chars' ? -40 : 0 }, {
      y: 0, opacity: 1, rotationX: 0,
      duration: splitBy === 'chars' ? 0.5 : 0.6,
      stagger: splitBy === 'chars' ? 0.03 : 0.08,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     5. TYPEWRITER EFFECT (data-animate="typewriter")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="typewriter"]').forEach(function (el) {
    var text = el.textContent;
    var speed = parseFloat(el.getAttribute('data-type-speed') || 0.04);
    el.textContent = '';
    el.style.opacity = 1;
    el.style.borderRight = '2px solid var(--color-primary, #3b82f6)';

    var obj = { length: 0 };
    gsap.to(obj, {
      length: text.length, duration: text.length * speed, ease: 'none', roundProps: 'length',
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' },
      onUpdate: function () { el.textContent = text.substring(0, obj.length); },
      onComplete: function () {
        gsap.to(el, { borderColor: 'transparent', repeat: -1, yoyo: true, duration: 0.6 });
      }
    });
  });

  /* ----------------------------------------------------------
     6. FLOATING ELEMENTS (data-animate="float")
     Continuous gentle floating motion
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="float"]').forEach(function (el) {
    el.style.opacity = 1;
    var range = parseFloat(el.getAttribute('data-float-range') || 15);
    var dur = parseFloat(el.getAttribute('data-float-speed') || 3);
    gsap.to(el, {
      y: -range, duration: dur, ease: 'sine.inOut', repeat: -1, yoyo: true,
      delay: Math.random() * 2
    });
    gsap.to(el, {
      x: range * 0.4, duration: dur * 1.3, ease: 'sine.inOut', repeat: -1, yoyo: true,
      delay: Math.random() * 2
    });
  });

  /* ----------------------------------------------------------
     7. COUNTER ANIMATION (data-counter="NUMBER")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-counter]').forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-counter'));
    var suffix = el.getAttribute('data-counter-suffix') || '';
    var prefix = el.getAttribute('data-counter-prefix') || '';
    var decimals = parseInt(el.getAttribute('data-counter-decimals') || 0);
    var dur = parseFloat(el.getAttribute('data-counter-duration') || 2.5);
    var obj = { val: 0 };

    gsap.to(obj, {
      val: target, duration: dur, ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 88%', toggleActions: 'play none none none' },
      onUpdate: function () {
        el.textContent = prefix + (decimals > 0 ? obj.val.toFixed(decimals) : Math.round(obj.val)) + suffix;
      }
    });
  });

  /* ----------------------------------------------------------
     8. MAGNETIC HOVER (data-animate="magnetic")
     Elements subtly follow cursor on hover
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="magnetic"]').forEach(function (el) {
    el.style.opacity = 1;
    var strength = parseFloat(el.getAttribute('data-magnetic-strength') || 0.3);
    el.addEventListener('mousemove', function (e) {
      var rect = el.getBoundingClientRect();
      var x = (e.clientX - rect.left - rect.width / 2) * strength;
      var y = (e.clientY - rect.top - rect.height / 2) * strength;
      gsap.to(el, { x: x, y: y, duration: 0.4, ease: 'power2.out' });
    });
    el.addEventListener('mouseleave', function () {
      gsap.to(el, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
    });
  });

  /* ----------------------------------------------------------
     9. 3D TILT ON HOVER (data-animate="tilt")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="tilt"]').forEach(function (el) {
    el.style.opacity = 1;
    el.style.transformStyle = 'preserve-3d';
    el.style.perspective = '800px';
    var maxTilt = parseFloat(el.getAttribute('data-tilt-max') || 12);

    el.addEventListener('mousemove', function (e) {
      var rect = el.getBoundingClientRect();
      var xPct = (e.clientX - rect.left) / rect.width - 0.5;
      var yPct = (e.clientY - rect.top) / rect.height - 0.5;
      gsap.to(el, {
        rotationY: xPct * maxTilt, rotationX: -yPct * maxTilt,
        transformPerspective: 800, duration: 0.4, ease: 'power2.out'
      });
    });
    el.addEventListener('mouseleave', function () {
      gsap.to(el, { rotationY: 0, rotationX: 0, duration: 0.6, ease: 'power2.out' });
    });
  });

  /* ----------------------------------------------------------
     10. GRADIENT FLOW (data-animate="gradient-flow")
     Animated shifting gradient background
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="gradient-flow"]').forEach(function (el) {
    el.style.opacity = 1;
    el.style.backgroundSize = '200% 200%';
    gsap.to(el, {
      backgroundPosition: '100% 100%', duration: 6, ease: 'sine.inOut',
      repeat: -1, yoyo: true
    });
  });

  /* ----------------------------------------------------------
     11. MARQUEE / INFINITE SCROLL (data-animate="marquee")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="marquee"]').forEach(function (el) {
    el.style.opacity = 1;
    var inner = el.querySelector('.marquee-inner');
    if (!inner) return;
    var speed = parseFloat(el.getAttribute('data-marquee-speed') || 30);
    var dir = el.getAttribute('data-marquee-direction') === 'right' ? 1 : -1;

    // Clone for seamless loop
    inner.innerHTML += inner.innerHTML;
    var w = inner.scrollWidth / 2;

    gsap.fromTo(inner,
      { x: dir > 0 ? -w : 0 },
      { x: dir > 0 ? 0 : -w, duration: speed, ease: 'none', repeat: -1 }
    );
  });

  /* ----------------------------------------------------------
     12. MORPHING BACKGROUND SHAPES (data-animate="morph-bg")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="morph-bg"]').forEach(function (el) {
    el.style.opacity = 1;
    var shapes = [
      '30% 70% 70% 30% / 30% 30% 70% 70%',
      '70% 30% 30% 70% / 70% 70% 30% 30%',
      '50% 50% 30% 70% / 60% 40% 60% 40%',
      '40% 60% 60% 40% / 30% 70% 30% 70%'
    ];
    var tl = gsap.timeline({ repeat: -1, yoyo: true });
    shapes.forEach(function (shape) {
      tl.to(el, { borderRadius: shape, duration: 4, ease: 'sine.inOut' });
    });
  });

  /* ----------------------------------------------------------
     13. SCROLL PROGRESS BAR (auto-created if data-scroll-progress exists)
     ---------------------------------------------------------- */
  var progressBar = document.querySelector('[data-scroll-progress]');
  if (progressBar) {
    gsap.to(progressBar, {
      scaleX: 1, ease: 'none',
      scrollTrigger: { trigger: document.body, start: 'top top', end: 'bottom bottom', scrub: 0.3 }
    });
    progressBar.style.transformOrigin = 'left center';
    progressBar.style.transform = 'scaleX(0)';
  }

  /* ----------------------------------------------------------
     14. IMAGE REVEAL ON SCROLL (data-animate="img-reveal")
     ---------------------------------------------------------- */
  document.querySelectorAll('.img-reveal-wrap').forEach(function (wrap) {
    var overlay = wrap.querySelector('.img-reveal-overlay');
    var img = wrap.querySelector('img');
    if (!overlay || !img) return;

    var tl = gsap.timeline({
      scrollTrigger: { trigger: wrap, start: 'top 80%', toggleActions: 'play none none none' }
    });
    tl.fromTo(overlay, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: 'power3.inOut', transformOrigin: 'left center' })
      .set(img, { opacity: 1 })
      .to(overlay, { scaleX: 0, duration: 0.6, ease: 'power3.inOut', transformOrigin: 'right center' });
  });

  /* ----------------------------------------------------------
     15. HORIZONTAL SCROLL SECTION (data-horizontal-scroll)
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-horizontal-scroll]').forEach(function (section) {
    var inner = section.querySelector('.hs-inner');
    if (!inner) return;
    var totalW = inner.scrollWidth - section.offsetWidth;

    gsap.to(inner, {
      x: -totalW, ease: 'none',
      scrollTrigger: {
        trigger: section, start: 'top top', end: function () { return '+=' + totalW; },
        scrub: 1, pin: true, anticipatePin: 1
      }
    });
  });

  /* ----------------------------------------------------------
     16. CURSOR GLOW EFFECT (auto if body has data-cursor-glow)
     ---------------------------------------------------------- */
  if (document.body.hasAttribute('data-cursor-glow')) {
    var glow = document.createElement('div');
    glow.className = 'cursor-glow';
    glow.style.cssText = 'position:fixed;width:300px;height:300px;border-radius:50%;pointer-events:none;z-index:9999;mix-blend-mode:screen;background:radial-gradient(circle,rgba(var(--color-primary-rgb,59,130,246),0.15),transparent 70%);transform:translate(-50%,-50%);transition:opacity 0.3s;opacity:0;';
    document.body.appendChild(glow);
    document.addEventListener('mousemove', function (e) {
      glow.style.opacity = '1';
      gsap.to(glow, { left: e.clientX, top: e.clientY, duration: 0.5, ease: 'power2.out' });
    });
  }

  /* ----------------------------------------------------------
     17. NAVBAR SCROLL BEHAVIOR
     ---------------------------------------------------------- */
  var nav = document.querySelector('[data-nav-scroll]');
  if (nav) {
    ScrollTrigger.create({
      start: 'top -80',
      onUpdate: function (self) {
        if (self.direction === 1) { gsap.to(nav, { y: -100, duration: 0.3 }); }
        else { gsap.to(nav, { y: 0, duration: 0.3 }); }
      }
    });
    ScrollTrigger.create({
      start: 'top -20',
      toggleClass: { targets: nav, className: 'nav-scrolled' }
    });
  }

  /* ----------------------------------------------------------
     18. HAMBURGER MENU
     ---------------------------------------------------------- */
  var menuBtn = document.getElementById('menu-toggle');
  var mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', function () {
      var opening = mobileMenu.classList.contains('hidden');
      mobileMenu.classList.toggle('hidden');
      menuBtn.setAttribute('aria-expanded', opening);
      if (opening) {
        gsap.fromTo(mobileMenu.children, { y: -20, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.05, duration: 0.3 });
      }
    });
  }

  /* ----------------------------------------------------------
     19. SMOOTH SCROLL
     ---------------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      var target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) mobileMenu.classList.add('hidden');
      }
    });
  });

  /* ----------------------------------------------------------
     20. LOADING REVEAL - fade out preloader
     ---------------------------------------------------------- */
  var preloader = document.getElementById('preloader');
  if (preloader) {
    gsap.to(preloader, {
      opacity: 0, duration: 0.6, delay: 0.2, ease: 'power2.inOut',
      onComplete: function () { preloader.style.display = 'none'; }
    });
  }
});
