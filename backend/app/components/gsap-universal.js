/* ============================================================
   GSAP Universal Animation Engine v3.0
   Auto-injected in every generated site
   Effects: parallax, text-split, typewriter, magnetic, 3D tilt,
   floating, gradient-flow, blur-in, curtain, morphing, glass,
   marquee, counter, stagger, scroll-progress, text-reveal,
   stagger-scale, clip-reveal, blur-slide, rotate-3d, image-zoom,
   card-hover-3d, draw-svg, split-screen
   Supports: data-delay, data-duration, data-ease on all animations
   Respects prefers-reduced-motion
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  // Fallback: if GSAP didn't load, show all content immediately
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    document.querySelectorAll('[data-animate]').forEach(function (el) {
      el.style.opacity = '1';
    });
    console.warn('[GSAP] Library not loaded, showing content without animations');
    return;
  }

  // === IFRAME DETECTION ===
  // Note: window.top throws SecurityError in sandbox iframe without allow-same-origin
  var isIframe = false;
  try { isIframe = window.self !== window.top; } catch (e) { isIframe = true; }

  // === LENIS SMOOTH SCROLL (skip in iframes — interferes with ScrollTrigger) ===
  var lenis = null;
  if (typeof Lenis !== 'undefined' && !isIframe) {
    lenis = new Lenis({
      duration: 1.2,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      direction: 'vertical',
      gestureDirection: 'vertical',
      smooth: true,
      smoothTouch: false,
      touchMultiplier: 2,
    });

    // Sync with GSAP ScrollTrigger
    lenis.on('scroll', function () {
      if (typeof ScrollTrigger !== 'undefined') {
        ScrollTrigger.update();
      }
    });

    gsap.ticker.add(function (time) {
      lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);
  }

  // === SMART NAVBAR (hide on scroll down, show on scroll up) ===
  var navEl = document.querySelector('nav, [data-nav]');
  if (navEl && typeof ScrollTrigger !== 'undefined') {
    var showNav = gsap.fromTo(navEl,
      { yPercent: 0 },
      { yPercent: -100, duration: 0.3, ease: 'power2.inOut', paused: true }
    );

    ScrollTrigger.create({
      start: 'top top',
      end: 'max',
      onUpdate: function (self) {
        if (self.direction === -1) {
          showNav.reverse();
        } else if (self.scroll() > 100) {
          showNav.play();
        }
      }
    });
  }

  // In iframe (editor preview): skip ALL scroll-triggered animations,
  // show all content immediately. Preview must display the full site.
  if (isIframe) {
    document.querySelectorAll('[data-animate]').forEach(function (el) {
      el.style.opacity = '1';
      el.style.transform = 'none';
      el.style.animation = 'none';
    });
    console.log('[GSAP] Iframe detected: scroll animations disabled, all content visible');
    return; // Skip everything — no scroll animations needed in editor preview
  }

  // Safety timeout: if animations haven't started after 3s, force-show content
  var _gsapInitialized = false;
  setTimeout(function () {
    if (!_gsapInitialized) {
      document.querySelectorAll('[data-animate]').forEach(function (el) {
        if (getComputedStyle(el).opacity === '0') {
          el.style.opacity = '1';
        }
      });
    }
  }, 3000);

  // Respect prefers-reduced-motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('reduced-motion');
    return; // Skip all animations
  }

  try {
  gsap.registerPlugin(ScrollTrigger);
  } catch (e) {
    console.warn('[GSAP] Failed to register plugins:', e);
    document.querySelectorAll('[data-animate]').forEach(function (el) { el.style.opacity = '1'; });
    return;
  }
  _gsapInitialized = true;

  // Cancel CSS fallback animation since GSAP is working
  document.querySelectorAll('[data-animate]').forEach(function (el) {
    el.style.animation = 'none';
  });

  // Mobile detection for reduced animation complexity
  var isMobile = window.innerWidth < 768 || ('ontouchstart' in window);

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
    if (['stagger', 'parallax', 'text-split', 'typewriter', 'float', 'marquee', 'tilt', 'magnetic', 'gradient-flow', 'morph-bg', 'text-reveal', 'stagger-scale', 'clip-reveal', 'blur-slide', 'rotate-3d', 'image-zoom', 'card-hover-3d', 'draw-svg', 'split-screen'].indexOf(type) !== -1) return;
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
    var delay = parseFloat(container.getAttribute('data-delay') || 0);
    var dur = parseFloat(container.getAttribute('data-duration') || 0.7);
    var easing = container.getAttribute('data-ease') || 'power3.out';
    var from = { opacity: 0 };
    if (effect === 'fade-up')    Object.assign(from, { y: 50 });
    if (effect === 'scale-in')   Object.assign(from, { scale: 0.7 });
    if (effect === 'blur-in')    Object.assign(from, { filter: 'blur(12px)', y: 20 });
    if (effect === 'slide-left') Object.assign(from, { x: -60 });

    gsap.fromTo(items, from, {
      y: 0, x: 0, scale: 1, opacity: 1, filter: 'blur(0px)',
      duration: dur, delay: delay, stagger: function(i) { return 0.12 * i + Math.random() * 0.08; },
      ease: easing,
      scrollTrigger: { trigger: container, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     2b. ORGANIC ENTROPY (controlled imperfection)
     Assigns random micro-rotation to stagger items and cards
     ---------------------------------------------------------- */
  document.querySelectorAll('.stagger-item, .bento-card, [data-entropy]').forEach(function (el) {
    el.style.setProperty('--entropy', (Math.random() * 2 - 1).toFixed(3));
    el.style.transform = 'rotate(calc(var(--entropy) * 1deg))';
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
    var splitBy = el.getAttribute('data-split-type') || el.getAttribute('data-split') || 'chars';
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = el.getAttribute('data-duration');
    var easing = el.getAttribute('data-ease') || 'power3.out';
    var text = el.textContent;
    el.innerHTML = '';
    el.style.opacity = 1;

    if (splitBy === 'lines') {
      // Wrap each line - use a temp container to measure
      var temp = document.createElement('div');
      temp.style.cssText = 'position:absolute;visibility:hidden;white-space:normal;width:' + el.offsetWidth + 'px;font:' + getComputedStyle(el).font;
      temp.textContent = text;
      document.body.appendChild(temp);
      document.body.removeChild(temp);
      // For lines, split by newlines or treat whole text as single line
      var lines = text.split('\n').filter(function (l) { return l.trim(); });
      if (lines.length <= 1) lines = [text];
      lines.forEach(function (line) {
        var span = document.createElement('span');
        span.textContent = line;
        span.style.display = 'block';
        span.style.opacity = '0';
        el.appendChild(span);
      });
    } else {
      var pieces = splitBy === 'words' ? text.split(/\s+/).filter(function(p) { return p.length > 0; }) : text.split('');
      pieces.forEach(function (piece, i) {
        var span = document.createElement('span');
        span.textContent = piece;
        span.style.display = 'inline-block';
        span.style.opacity = '0';
        // Add margin-right for word spacing (except last word)
        if (splitBy === 'words' && i < pieces.length - 1) {
          span.style.marginRight = '0.3em';
        }
        el.appendChild(span);
      });
    }

    var defaultDur = splitBy === 'chars' ? 0.5 : (splitBy === 'lines' ? 0.7 : 0.6);
    var defaultStagger = splitBy === 'chars' ? 0.03 : (splitBy === 'lines' ? 0.1 : 0.08);

    gsap.fromTo(el.children, { y: splitBy === 'words' ? 30 : (splitBy === 'lines' ? 40 : 15), opacity: 0, rotationX: splitBy === 'chars' ? -40 : 0 }, {
      y: 0, opacity: 1, rotationX: 0,
      duration: dur ? parseFloat(dur) : defaultDur,
      delay: delay,
      stagger: defaultStagger,
      ease: easing,
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     5. TYPEWRITER EFFECT (data-animate="typewriter")
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="typewriter"]').forEach(function (el) {
    var text = el.textContent;
    var speed = parseFloat(el.getAttribute('data-type-speed') || 0.04);
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = el.getAttribute('data-duration') ? parseFloat(el.getAttribute('data-duration')) : text.length * speed;
    var easing = el.getAttribute('data-ease') || 'none';
    el.textContent = '';
    el.style.opacity = 1;
    el.style.borderRight = '2px solid var(--color-primary, #3b82f6)';

    var obj = { length: 0 };
    gsap.to(obj, {
      length: text.length, duration: dur, delay: delay, ease: easing, roundProps: 'length',
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' },
      onUpdate: function () { el.textContent = text.substring(0, obj.length); },
      onComplete: function () {
        gsap.to(el, { borderColor: 'transparent', repeat: -1, yoyo: true, duration: 0.6 });
      }
    });
  });

  /* ----------------------------------------------------------
     6. FLOATING ELEMENTS (data-animate="float")
     Continuous gentle floating motion (reduced on mobile)
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="float"]').forEach(function (el) {
    el.style.opacity = 1;
    var range = parseFloat(el.getAttribute('data-float-range') || 15);
    var dur = parseFloat(el.getAttribute('data-duration') || el.getAttribute('data-float-speed') || 3);
    var baseDelay = parseFloat(el.getAttribute('data-delay') || 0);
    var easing = el.getAttribute('data-ease') || 'sine.inOut';
    // Reduce float range and skip horizontal axis on mobile for performance
    var mobileRange = isMobile ? range * 0.5 : range;
    gsap.to(el, {
      y: -mobileRange, duration: dur, ease: easing, repeat: -1, yoyo: true,
      delay: baseDelay + Math.random() * 2
    });
    if (!isMobile) {
      gsap.to(el, {
        x: range * 0.4, duration: dur * 1.3, ease: easing, repeat: -1, yoyo: true,
        delay: baseDelay + Math.random() * 2
      });
    }
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
     Skipped on mobile (no mousemove)
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="tilt"]').forEach(function (el) {
    el.style.opacity = 1;
    if (isMobile) return; // Skip tilt on touch devices
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
     9b. CARD BORDER GLOW (Linear-style hover glow on borders)
     Adds a radial-gradient overlay on card borders that follows the mouse.
     Applied to tilt and card-hover-3d elements. Desktop only.
     ---------------------------------------------------------- */
  if (window.matchMedia('(hover: hover)').matches && window.innerWidth > 768) {
    document.querySelectorAll('[data-animate="tilt"], [data-animate="card-hover-3d"]').forEach(function (el) {
      // Ensure positioning context
      if (!el.style.position || el.style.position === 'static') {
        el.style.position = 'relative';
      }
      el.style.overflow = 'hidden';

      var glowEl = document.createElement('div');
      glowEl.className = 'card-border-glow';
      el.appendChild(glowEl);

      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        glowEl.style.setProperty('--mouse-x', x + 'px');
        glowEl.style.setProperty('--mouse-y', y + 'px');
        glowEl.style.opacity = '1';
      });

      el.addEventListener('mouseleave', function () {
        glowEl.style.opacity = '0';
      });
    });
  }

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
     13. TEXT REVEAL (data-animate="text-reveal")
     Lines slide up from below a clip-path mask
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="text-reveal"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 0.8);
    var easing = el.getAttribute('data-ease') || 'power3.out';
    var text = el.textContent;
    var lines = text.split('\n').filter(function (l) { return l.trim(); });
    if (lines.length <= 1) lines = [text];
    el.innerHTML = '';
    el.style.opacity = 1;

    lines.forEach(function (line) {
      var wrapper = document.createElement('div');
      wrapper.style.overflow = 'hidden';
      wrapper.style.display = 'block';
      var inner = document.createElement('div');
      inner.textContent = line;
      inner.style.transform = 'translateY(100%)';
      wrapper.appendChild(inner);
      el.appendChild(wrapper);
    });

    var innerDivs = el.querySelectorAll('div > div');
    gsap.fromTo(innerDivs, { y: '100%' }, {
      y: '0%', duration: dur, delay: delay, ease: easing,
      stagger: 0.12,
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     14. STAGGER SCALE (data-animate="stagger-scale")
     Children scale from 0 to 1 with stagger
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="stagger-scale"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 0.6);
    var easing = el.getAttribute('data-ease') || 'back.out(1.7)';
    el.style.opacity = 1;

    gsap.from(el.children, {
      scale: 0, duration: dur, delay: delay, ease: easing,
      stagger: 0.1,
      scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
    });
  });

  /* ----------------------------------------------------------
     15. CLIP REVEAL (data-animate="clip-reveal")
     Section reveals via expanding clip-path from center
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="clip-reveal"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 1.2);
    var easing = el.getAttribute('data-ease') || 'power3.inOut';

    gsap.fromTo(el,
      { clipPath: 'circle(0% at 50% 50%)' },
      {
        clipPath: 'circle(100% at 50% 50%)', duration: dur, delay: delay, ease: easing,
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
      }
    );
  });

  /* ----------------------------------------------------------
     16. BLUR SLIDE (data-animate="blur-slide")
     Dreamy entrance: blur + translateY
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="blur-slide"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 1);
    var easing = el.getAttribute('data-ease') || 'power3.out';

    gsap.fromTo(el,
      { filter: 'blur(20px)', y: 40, opacity: 0 },
      {
        filter: 'blur(0px)', y: 0, opacity: 1,
        duration: dur, delay: delay, ease: easing,
        scrollTrigger: { trigger: el, start: 'top 88%', toggleActions: 'play none none none' }
      }
    );
  });

  /* ----------------------------------------------------------
     17. ROTATE 3D (data-animate="rotate-3d")
     Card flipping toward viewer on X axis
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="rotate-3d"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 0.9);
    var easing = el.getAttribute('data-ease') || 'power3.out';

    gsap.fromTo(el,
      { rotationX: -15, opacity: 0, transformPerspective: 800 },
      {
        rotationX: 0, opacity: 1, transformPerspective: 800,
        duration: dur, delay: delay, ease: easing,
        scrollTrigger: { trigger: el, start: 'top 88%', toggleActions: 'play none none none' }
      }
    );
  });

  /* ----------------------------------------------------------
     18. IMAGE ZOOM (data-animate="image-zoom")
     Image scales on scroll inside overflow:hidden container
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="image-zoom"]').forEach(function (el) {
    el.style.overflow = 'hidden';
    var img = el.querySelector('img');
    if (!img) return;

    gsap.fromTo(img,
      { scale: 1 },
      {
        scale: 1.15, ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 }
      }
    );
  });

  /* ----------------------------------------------------------
     19. CARD HOVER 3D (data-animate="card-hover-3d")
     3D perspective tilt on mousemove with light reflection
     Skipped on mobile (no mousemove)
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="card-hover-3d"]').forEach(function (el) {
    el.style.opacity = 1;
    if (isMobile) return; // Skip 3D hover on touch devices
    el.style.transformStyle = 'preserve-3d';
    el.style.perspective = '800px';
    el.style.position = el.style.position || 'relative';
    el.style.overflow = 'hidden';

    // Create light reflection div
    var reflection = document.createElement('div');
    reflection.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;background:radial-gradient(circle at 50% 50%,rgba(255,255,255,0.15),transparent 60%);opacity:0;transition:opacity 0.3s;z-index:10;';
    el.appendChild(reflection);

    el.addEventListener('mousemove', function (e) {
      var rect = el.getBoundingClientRect();
      var xPct = (e.clientX - rect.left) / rect.width;
      var yPct = (e.clientY - rect.top) / rect.height;
      var rotateY = (xPct - 0.5) * 20;
      var rotateX = (0.5 - yPct) * 20;

      gsap.to(el, {
        rotationY: rotateY, rotationX: rotateX,
        transformPerspective: 800, duration: 0.4, ease: 'power2.out'
      });

      reflection.style.opacity = '1';
      reflection.style.background = 'radial-gradient(circle at ' + (xPct * 100) + '% ' + (yPct * 100) + '%, rgba(255,255,255,0.2), transparent 60%)';
    });

    el.addEventListener('mouseleave', function () {
      gsap.to(el, { rotationY: 0, rotationX: 0, duration: 0.6, ease: 'power2.out' });
      reflection.style.opacity = '0';
    });
  });

  /* ----------------------------------------------------------
     20. DRAW SVG (data-animate="draw-svg")
     SVG stroke animation on scroll
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="draw-svg"]').forEach(function (el) {
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 2);
    var easing = el.getAttribute('data-ease') || 'power2.inOut';
    var paths = el.querySelectorAll('path, line, polyline, polygon, circle, ellipse, rect');

    paths.forEach(function (path) {
      var length = path.getTotalLength ? path.getTotalLength() : 0;
      if (!length) return;
      path.style.strokeDasharray = length;
      path.style.strokeDashoffset = length;

      gsap.to(path, {
        strokeDashoffset: 0, duration: dur, delay: delay, ease: easing,
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
      });
    });
  });

  /* ----------------------------------------------------------
     21. SPLIT SCREEN (data-animate="split-screen")
     Two child divs animate apart on scroll
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="split-screen"]').forEach(function (el) {
    var left = el.querySelector('.left');
    var right = el.querySelector('.right');
    if (!left || !right) return;

    gsap.fromTo(left,
      { x: '0%' },
      {
        x: '-50%', ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 }
      }
    );
    gsap.fromTo(right,
      { x: '0%' },
      {
        x: '50%', ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 }
      }
    );
  });

  /* ----------------------------------------------------------
     22. SCROLL PROGRESS BAR (auto-created if data-scroll-progress exists)
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
     23. IMAGE REVEAL ON SCROLL (data-animate="img-reveal")
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
     24. HORIZONTAL SCROLL SECTION (data-horizontal-scroll)
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
     25. GLOBAL CURSOR GLOW (desktop only, always active)
     Uses gsap.quickTo for buttery smooth 60fps performance
     ---------------------------------------------------------- */
  if (window.matchMedia('(hover: hover)').matches && window.innerWidth > 768) {
    var glow = document.createElement('div');
    glow.className = 'cursor-glow';
    document.body.appendChild(glow);

    // gsap.quickTo avoids creating new tweens on every mousemove
    var xTo = gsap.quickTo(glow, 'left', { duration: 0.6, ease: 'power3.out' });
    var yTo = gsap.quickTo(glow, 'top', { duration: 0.6, ease: 'power3.out' });

    document.addEventListener('mousemove', function (e) {
      xTo(e.clientX);
      yTo(e.clientY);
      if (!glow.classList.contains('active')) {
        glow.classList.add('active');
      }
    });

    // Hide when mouse leaves the window
    document.addEventListener('mouseleave', function () {
      glow.classList.remove('active');
    });
    document.addEventListener('mouseenter', function () {
      glow.classList.add('active');
    });
  }

  /* ----------------------------------------------------------
     26. NAVBAR SCROLL BEHAVIOR
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
     27. HAMBURGER MENU
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
     28. SMOOTH SCROLL
     ---------------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      var target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        if (lenis) {
          lenis.scrollTo(target, { offset: 0 });
        } else {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) mobileMenu.classList.add('hidden');
      }
    });
  });

  /* ----------------------------------------------------------
     29. LOADING REVEAL - fade out preloader
     ---------------------------------------------------------- */
  var preloader = document.getElementById('preloader');
  if (preloader) {
    gsap.to(preloader, {
      opacity: 0, duration: 0.6, delay: 0.2, ease: 'power2.inOut',
      onComplete: function () { preloader.style.display = 'none'; }
    });
  }

});
