/* ============================================================
   GSAP Universal Animation Engine v4.0
   Auto-injected in every generated site
   Effects: parallax, text-split, typewriter, magnetic, 3D tilt,
   floating, gradient-flow, blur-in, curtain, morphing, glass,
   marquee, counter, stagger, scroll-progress, text-reveal,
   stagger-scale, clip-reveal, blur-slide, rotate-3d, image-zoom,
   card-hover-3d, draw-svg, split-screen, scroll-fade, pin-hero,
   section-reveal, text-rotate, sticky-cta, sticky-reveal,
   before-after, section-progress, parallax-layers, 3d-scroll,
   scroll-snap-horizontal, data-parallax (standalone),
   ---- v4.0 NEW ----
   text-fill, border-beam, spotlight, shimmer, ripple,
   infinite-cards, number-ticker, particles-bg
   + CSS Scroll-Driven Animations native layer
   Supports: data-delay, data-duration, data-ease, data-scrub
   Respects prefers-reduced-motion
   Skips heavy scroll effects on mobile/touch
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

  // Per-style animation speed multiplier (set via --animation-speed CSS variable)
  var _animSpeed = parseFloat(getComputedStyle(document.body).getPropertyValue('--animation-speed')) || 1;

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
    if (['stagger', 'parallax', 'text-split', 'typewriter', 'text-rotate', 'float', 'marquee', 'tilt', 'magnetic', 'gradient-flow', 'morph-bg', 'text-reveal', 'stagger-scale', 'clip-reveal', 'blur-slide', 'rotate-3d', 'image-zoom', 'card-hover-3d', 'draw-svg', 'split-screen', 'scroll-fade', 'pin-hero', 'section-reveal', 'sticky-cta', 'sticky-reveal', 'before-after', 'section-progress', 'parallax-layers', '3d-scroll', 'scroll-snap-horizontal', 'text-fill', 'border-beam', 'spotlight', 'shimmer', 'ripple', 'infinite-cards', 'number-ticker', 'particles-bg'].indexOf(type) !== -1) return;
    var config = animations[type];
    if (!config) { el.style.opacity = 1; return; }

    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 0.9) * _animSpeed;
    var easing = el.getAttribute('data-ease') || (type === 'bounce-in' ? 'elastic.out(1,0.5)' : 'power3.out');

    gsap.fromTo(el, Object.assign({}, config), {
      y: 0, x: 0, scale: 1, opacity: 1, rotation: 0, rotationX: 0,
      filter: 'blur(0px)',
      clipPath: 'inset(0 0% 0 0)',
      duration: dur, delay: delay * _animSpeed, ease: easing,
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
    var dur = parseFloat(container.getAttribute('data-duration') || 0.8) * _animSpeed;
    var easing = container.getAttribute('data-ease') || 'power3.out';
    var from = { opacity: 0 };
    if (effect === 'fade-up')    Object.assign(from, { y: 30, filter: 'blur(6px)' });
    if (effect === 'scale-in')   Object.assign(from, { scale: 0.7, filter: 'blur(4px)' });
    if (effect === 'blur-in')    Object.assign(from, { filter: 'blur(16px)', y: 30 });
    if (effect === 'slide-left') Object.assign(from, { x: -60, filter: 'blur(4px)' });

    gsap.fromTo(items, from, {
      y: 0, x: 0, scale: 1, opacity: 1, filter: 'blur(0px)',
      duration: dur, delay: delay * _animSpeed,
      stagger: function(i) { return (0.12 * i + Math.random() * 0.1) * _animSpeed; },
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
     3. PARALLAX SCROLLING (data-animate="parallax" or data-parallax)
     Skip on mobile/touch for performance
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="parallax"]').forEach(function (el) {
      var speed = parseFloat(el.getAttribute('data-speed') || el.getAttribute('data-parallax') || 0.3);
      var direction = el.getAttribute('data-direction') || 'y';
      gsap.to(el, {
        y: direction === 'y' ? speed * -200 : 0,
        x: direction === 'x' ? speed * -200 : 0,
        ease: 'none',
        scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: 1.5 }
      });
    });

    // Standalone data-parallax attribute (any element, not just data-animate="parallax")
    document.querySelectorAll('[data-parallax]:not([data-animate="parallax"])').forEach(function (el) {
      var speed = parseFloat(el.getAttribute('data-parallax') || 0.3);
      gsap.to(el, {
        yPercent: -speed * 100,
        ease: 'none',
        scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: 1 }
      });
    });
  } else {
    // On mobile, just show parallax elements without scroll effect
    document.querySelectorAll('[data-animate="parallax"], [data-parallax]').forEach(function (el) {
      el.style.opacity = '1';
    });
  }

  /* ----------------------------------------------------------
     3b. SCROLL-LINKED FADE (data-animate="scroll-fade")
     Element opacity fades out as user scrolls past it.
     Great for hero text that dissolves on scroll.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="scroll-fade"]').forEach(function (el) {
    el.style.opacity = '1';
    var startTrigger = el.getAttribute('data-fade-start') || 'top top';
    var endTrigger = el.getAttribute('data-fade-end') || 'bottom top';
    gsap.fromTo(el,
      { opacity: 1 },
      {
        opacity: 0, ease: 'none',
        scrollTrigger: { trigger: el, start: startTrigger, end: endTrigger, scrub: true }
      }
    );
  });

  /* ----------------------------------------------------------
     3c. PIN HERO (data-animate="pin-hero")
     Pins the hero section while content scrolls over it.
     Desktop only — on mobile it just displays normally.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="pin-hero"]').forEach(function (el) {
      el.style.opacity = '1';
      el.style.zIndex = '0';
      var pinDuration = el.getAttribute('data-pin-duration') || '100%';
      ScrollTrigger.create({
        trigger: el,
        start: 'top top',
        end: '+=' + pinDuration,
        pin: true,
        pinSpacing: false,
        scrub: true
      });
      // Optional: fade out as content scrolls over
      if (el.getAttribute('data-pin-fade') !== 'false') {
        gsap.to(el, {
          opacity: 0.3,
          ease: 'none',
          scrollTrigger: { trigger: el, start: 'top top', end: '+=' + pinDuration, scrub: true }
        });
      }
    });
  } else {
    document.querySelectorAll('[data-animate="pin-hero"]').forEach(function (el) {
      el.style.opacity = '1';
    });
  }

  /* ----------------------------------------------------------
     3d. SECTION REVEAL (data-animate="section-reveal")
     Sections reveal via clip-path inset that opens on scroll.
     Gives a "curtain opening" effect. Desktop only.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="section-reveal"]').forEach(function (el) {
      gsap.fromTo(el,
        { clipPath: 'inset(10% 0 10% 0)' },
        {
          clipPath: 'inset(0% 0% 0% 0%)', ease: 'none',
          scrollTrigger: { trigger: el, start: 'top 90%', end: 'top 40%', scrub: 1 }
        }
      );
    });
  } else {
    document.querySelectorAll('[data-animate="section-reveal"]').forEach(function (el) {
      el.style.opacity = '1';
    });
  }

  /* ----------------------------------------------------------
     4. TEXT SPLIT ANIMATION (data-animate="text-split")
     Splits text into chars/words and animates them
     Supports data-scrub="true" for scroll-linked character reveal
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

    var useScrub = el.getAttribute('data-scrub') === 'true';
    var defaultDur = splitBy === 'chars' ? 0.5 : (splitBy === 'lines' ? 0.7 : 0.6);
    var defaultStagger = splitBy === 'chars' ? 0.03 : (splitBy === 'lines' ? 0.1 : 0.08);

    if (useScrub) {
      // Scrub mode: characters reveal as you scroll through the section
      gsap.fromTo(el.children, { y: 10, opacity: 0 }, {
        y: 0, opacity: 1,
        stagger: defaultStagger,
        ease: 'none',
        scrollTrigger: { trigger: el, start: 'top 80%', end: 'top 30%', scrub: 1 }
      });
    } else {
      gsap.fromTo(el.children, { y: splitBy === 'words' ? 30 : (splitBy === 'lines' ? 40 : 15), opacity: 0, rotationX: splitBy === 'chars' ? -40 : 0 }, {
        y: 0, opacity: 1, rotationX: 0,
        duration: dur ? parseFloat(dur) : defaultDur,
        delay: delay,
        stagger: defaultStagger,
        ease: easing,
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
      });
    }
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
     5b. TEXT ROTATE (data-animate="text-rotate")
     Cycles through phrases with fade in/out loop.
     Reads data-rotate-texts="phrase1|phrase2|phrase3"
     Supports data-rotate-speed for hold duration (default 2.5s)
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="text-rotate"]').forEach(function (el) {
    var raw = el.getAttribute('data-rotate-texts') || el.textContent;
    var phrases = raw.split('|').map(function (s) { return s.trim(); }).filter(function (s) { return s.length > 0; });
    if (phrases.length === 0) return;
    el.textContent = phrases[0];
    el.style.opacity = 1;
    if (phrases.length < 2) return;

    var hold = parseFloat(el.getAttribute('data-rotate-speed') || 2.5);
    var tl = gsap.timeline({ repeat: -1 });
    for (var i = 0; i < phrases.length; i++) {
      (function (index) {
        tl.to(el, { opacity: 1, duration: 0.4, ease: 'power2.out',
          onStart: function () { el.textContent = phrases[index]; }
        });
        tl.to({}, { duration: hold });
        tl.to(el, { opacity: 0, duration: 0.4, ease: 'power2.in' });
      })(i);
    }
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
    var rawAttr = el.getAttribute('data-counter');
    var target, suffix, prefix;

    // Auto-parse: if data-counter is empty or "auto", extract number from textContent
    if (!rawAttr || rawAttr === '' || rawAttr === 'auto') {
      var content = el.textContent.trim();
      var numMatch = content.match(/[\d.,]+/);
      if (!numMatch) { el.style.opacity = '1'; return; }
      target = parseFloat(numMatch[0].replace(/\./g, '').replace(',', '.'));
      // Detect prefix (before the number) and suffix (after the number)
      var numIdx = content.indexOf(numMatch[0]);
      prefix = content.substring(0, numIdx).trim();
      suffix = content.substring(numIdx + numMatch[0].length).trim();
    } else {
      target = parseFloat(rawAttr);
      suffix = el.getAttribute('data-counter-suffix') || '';
      prefix = el.getAttribute('data-counter-prefix') || '';
    }

    var decimals = parseInt(el.getAttribute('data-counter-decimals') || 0);
    var dur = parseFloat(el.getAttribute('data-counter-duration') || 2);
    var useSeparator = el.getAttribute('data-counter-separator') !== 'false';
    var obj = { val: 0 };

    function formatNumber(num, dec) {
      var fixed = dec > 0 ? num.toFixed(dec) : Math.round(num).toString();
      if (!useSeparator) return fixed;
      var parts = fixed.split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
      return parts.join(',');
    }

    gsap.to(obj, {
      val: target, duration: dur, ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 88%', toggleActions: 'play none none none' },
      onUpdate: function () {
        el.textContent = prefix + formatNumber(obj.val, decimals) + suffix;
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
     28b. STICKY CTA BUTTON (data-animate="sticky-cta")
     Fixed button appears after scrolling 50vh, hides near footer.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="sticky-cta"]').forEach(function (el) {
    el.style.position = 'fixed';
    el.style.bottom = isMobile ? '1rem' : '2rem';
    el.style.right = isMobile ? '1rem' : '2rem';
    if (isMobile) { el.style.left = '1rem'; el.style.textAlign = 'center'; }
    el.style.zIndex = '50';
    el.style.backdropFilter = 'blur(8px)';
    el.style.webkitBackdropFilter = 'blur(8px)';
    gsap.set(el, { opacity: 0, y: 20 });

    ScrollTrigger.create({
      start: '50vh top',
      onEnter: function () { gsap.to(el, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }); },
      onLeaveBack: function () { gsap.to(el, { opacity: 0, y: 20, duration: 0.3, ease: 'power2.in' }); }
    });

    var footer = document.querySelector('footer');
    if (footer) {
      ScrollTrigger.create({
        trigger: footer,
        start: 'top bottom-=100',
        onEnter: function () { gsap.to(el, { opacity: 0, y: 20, duration: 0.3, ease: 'power2.in' }); },
        onLeaveBack: function () { gsap.to(el, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }); }
      });
    }
  });

  /* ----------------------------------------------------------
     30. STICKY REVEAL (data-animate="sticky-reveal")
     Section is pinned while inner .sticky-content children
     scroll through sequentially. Desktop only.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="sticky-reveal"]').forEach(function (el) {
      el.style.opacity = '1';
      var content = el.querySelector('.sticky-content');
      if (!content) return;
      var children = content.children;
      if (!children.length) return;

      var stickyDuration = el.getAttribute('data-sticky-duration') || '200%';

      // Pin the container
      ScrollTrigger.create({
        trigger: el,
        start: 'top top',
        end: '+=' + stickyDuration,
        pin: true,
        pinSpacing: true
      });

      // Animate each child: fade in then fade out as the next one appears
      var totalChildren = children.length;
      for (var i = 0; i < totalChildren; i++) {
        (function (index) {
          var child = children[index];
          var segmentStart = index / totalChildren;
          var segmentEnd = (index + 1) / totalChildren;
          var fadeInEnd = segmentStart + (segmentEnd - segmentStart) * 0.3;
          var fadeOutStart = segmentStart + (segmentEnd - segmentStart) * 0.7;

          // Initial state: hidden (except first)
          if (index > 0) {
            gsap.set(child, { opacity: 0, y: 30 });
          } else {
            gsap.set(child, { opacity: 1, y: 0 });
          }

          // Fade in
          if (index > 0) {
            gsap.fromTo(child,
              { opacity: 0, y: 30 },
              {
                opacity: 1, y: 0, ease: 'power2.out',
                scrollTrigger: {
                  trigger: el,
                  start: 'top top',
                  end: '+=' + stickyDuration,
                  scrub: true,
                  // Map to segment of the total scroll
                  onUpdate: function (self) {
                    var progress = self.progress;
                    if (progress >= segmentStart && progress <= fadeInEnd) {
                      var localProgress = (progress - segmentStart) / (fadeInEnd - segmentStart);
                      gsap.set(child, { opacity: localProgress, y: 30 * (1 - localProgress) });
                    }
                  }
                }
              }
            );
          }

          // Fade out (except last)
          if (index < totalChildren - 1) {
            ScrollTrigger.create({
              trigger: el,
              start: 'top top',
              end: '+=' + stickyDuration,
              scrub: true,
              onUpdate: function (self) {
                var progress = self.progress;
                if (progress >= fadeOutStart && progress <= segmentEnd) {
                  var localProgress = (progress - fadeOutStart) / (segmentEnd - fadeOutStart);
                  gsap.set(child, { opacity: 1 - localProgress, y: -20 * localProgress });
                }
              }
            });
          }
        })(i);
      }
    });
  } else {
    // Mobile: show all children stacked normally
    document.querySelectorAll('[data-animate="sticky-reveal"]').forEach(function (el) {
      el.style.opacity = '1';
      var content = el.querySelector('.sticky-content');
      if (!content) return;
      Array.prototype.forEach.call(content.children, function (child) {
        child.style.opacity = '1';
        child.style.transform = 'none';
      });
    });
  }

  /* ----------------------------------------------------------
     31. BEFORE-AFTER SLIDER (data-animate="before-after")
     Comparison slider with .before and .after child divs.
     Works with both mouse drag and touch.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="before-after"]').forEach(function (el) {
    el.style.opacity = '1';
    var beforeEl = el.querySelector('.before');
    var afterEl = el.querySelector('.after');
    var slider = el.querySelector('.ba-slider');
    if (!beforeEl || !afterEl) return;

    // Create slider handle if not present
    if (!slider) {
      slider = document.createElement('div');
      slider.className = 'ba-slider';
      slider.style.cssText = 'position:absolute;top:0;width:3px;height:100%;background:white;cursor:ew-resize;z-index:10;transform:translateX(-50%);box-shadow:0 0 8px rgba(0,0,0,0.3);';
      // Add drag handle circle
      var handle = document.createElement('div');
      handle.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:36px;height:36px;border-radius:50%;background:white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;';
      handle.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M5 3L1 8L5 13M11 3L15 8L11 13" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      slider.appendChild(handle);
      el.appendChild(slider);
    }

    // Setup positioning
    el.style.position = 'relative';
    el.style.overflow = 'hidden';
    el.style.userSelect = 'none';
    afterEl.style.position = 'absolute';
    afterEl.style.top = '0';
    afterEl.style.left = '0';
    afterEl.style.width = '100%';
    afterEl.style.height = '100%';

    var startPos = parseFloat(el.getAttribute('data-ba-start') || 50);
    var isDragging = false;

    function setPosition(pct) {
      pct = Math.max(0, Math.min(100, pct));
      beforeEl.style.clipPath = 'inset(0 ' + (100 - pct) + '% 0 0)';
      slider.style.left = pct + '%';
    }

    setPosition(startPos);

    function getPercent(clientX) {
      var rect = el.getBoundingClientRect();
      return ((clientX - rect.left) / rect.width) * 100;
    }

    // Mouse events
    slider.addEventListener('mousedown', function (e) {
      e.preventDefault();
      isDragging = true;
    });
    document.addEventListener('mousemove', function (e) {
      if (!isDragging) return;
      setPosition(getPercent(e.clientX));
    });
    document.addEventListener('mouseup', function () {
      isDragging = false;
    });

    // Touch events
    slider.addEventListener('touchstart', function (e) {
      isDragging = true;
    }, { passive: true });
    document.addEventListener('touchmove', function (e) {
      if (!isDragging) return;
      setPosition(getPercent(e.touches[0].clientX));
    }, { passive: true });
    document.addEventListener('touchend', function () {
      isDragging = false;
    });

    // Click anywhere on container to move slider
    el.addEventListener('click', function (e) {
      if (e.target === slider || slider.contains(e.target)) return;
      setPosition(getPercent(e.clientX));
    });
  });

  /* ----------------------------------------------------------
     32. SECTION SCROLL PROGRESS (data-animate="section-progress")
     Progress bar scoped to a specific section.
     Bar width goes from 0% to 100% as section scrolls through.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="section-progress"]').forEach(function (el) {
    el.style.opacity = '1';
    var position = el.getAttribute('data-progress-position') || 'top';
    var delay = parseFloat(el.getAttribute('data-delay') || 0);

    // Find or create progress bar
    var bar = el.querySelector('.section-progress-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'section-progress-bar';
      bar.style.cssText = 'position:absolute;left:0;height:3px;width:0%;background:var(--color-primary, #3b82f6);z-index:10;transition:none;';
      if (!el.style.position || el.style.position === 'static') {
        el.style.position = 'relative';
      }
      el.appendChild(bar);
    }

    bar.style[position] = '0';
    bar.style.width = '0%';

    ScrollTrigger.create({
      trigger: el,
      start: 'top bottom',
      end: 'bottom top',
      scrub: true,
      onUpdate: function (self) {
        bar.style.width = (self.progress * 100) + '%';
      }
    });
  });

  /* ----------------------------------------------------------
     33. PARALLAX LAYERS (data-animate="parallax-layers")
     Multiple .parallax-layer children move at different speeds.
     Desktop only.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="parallax-layers"]').forEach(function (el) {
      el.style.opacity = '1';
      var layers = el.querySelectorAll('.parallax-layer');
      if (!layers.length) return;

      layers.forEach(function (layer) {
        var speed = parseFloat(layer.getAttribute('data-speed') || 0.3);
        var yDistance = speed * -200;

        gsap.fromTo(layer,
          { y: -yDistance / 2 },
          {
            y: yDistance / 2,
            ease: 'none',
            scrollTrigger: {
              trigger: el,
              start: 'top bottom',
              end: 'bottom top',
              scrub: 1.5
            }
          }
        );
      });
    });
  } else {
    document.querySelectorAll('[data-animate="parallax-layers"]').forEach(function (el) {
      el.style.opacity = '1';
      var layers = el.querySelectorAll('.parallax-layer');
      layers.forEach(function (layer) {
        layer.style.opacity = '1';
        layer.style.transform = 'none';
      });
    });
  }

  /* ----------------------------------------------------------
     34. 3D SCROLL ROTATION (data-animate="3d-scroll")
     Element rotates on Y axis linked to scroll position.
     Desktop only.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="3d-scroll"]').forEach(function (el) {
      el.style.opacity = '1';
      var maxRot = parseFloat(el.getAttribute('data-rotation-max') || 15);
      var delay = parseFloat(el.getAttribute('data-delay') || 0);
      var dur = parseFloat(el.getAttribute('data-duration') || 1);
      var easing = el.getAttribute('data-ease') || 'none';

      el.style.perspective = '800px';
      el.style.transformStyle = 'preserve-3d';

      gsap.fromTo(el,
        { rotationY: -maxRot, transformPerspective: 800 },
        {
          rotationY: maxRot,
          transformPerspective: 800,
          ease: easing,
          scrollTrigger: {
            trigger: el,
            start: 'top bottom',
            end: 'bottom top',
            scrub: 1
          }
        }
      );
    });
  } else {
    document.querySelectorAll('[data-animate="3d-scroll"]').forEach(function (el) {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  }

  /* ----------------------------------------------------------
     35. SCROLL SNAP HORIZONTAL (data-animate="scroll-snap-horizontal")
     Horizontal scrolling section with CSS snap points.
     Optional autoplay with pause on hover/touch.
     Works on mobile via native CSS scroll snap.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="scroll-snap-horizontal"]').forEach(function (el) {
    el.style.opacity = '1';

    // Apply scroll-snap CSS to container
    el.style.overflowX = 'auto';
    el.style.overflowY = 'hidden';
    el.style.scrollSnapType = 'x mandatory';
    el.style.display = 'flex';
    el.style.webkitOverflowScrolling = 'touch'; // smooth on iOS
    el.style.scrollBehavior = 'smooth';
    // Hide scrollbar
    el.style.scrollbarWidth = 'none'; // Firefox
    el.style.msOverflowStyle = 'none'; // IE/Edge

    // Apply snap alignment to children
    var items = el.querySelectorAll('.snap-item');
    items.forEach(function (item) {
      item.style.scrollSnapAlign = 'start';
      item.style.flexShrink = '0';
    });

    // Autoplay functionality
    var autoplay = el.getAttribute('data-autoplay') === 'true';
    if (autoplay && items.length > 1) {
      var speed = parseFloat(el.getAttribute('data-autoplay-speed') || 5) * 1000;
      var currentIndex = 0;
      var autoplayTimer = null;
      var isPaused = false;

      function advanceSlide() {
        if (isPaused) return;
        currentIndex = (currentIndex + 1) % items.length;
        items[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
      }

      function startAutoplay() {
        if (autoplayTimer) clearInterval(autoplayTimer);
        autoplayTimer = setInterval(advanceSlide, speed);
      }

      function stopAutoplay() {
        isPaused = true;
        if (autoplayTimer) clearInterval(autoplayTimer);
      }

      function resumeAutoplay() {
        isPaused = false;
        startAutoplay();
      }

      // Pause on hover (desktop)
      el.addEventListener('mouseenter', stopAutoplay);
      el.addEventListener('mouseleave', resumeAutoplay);

      // Pause on touch
      el.addEventListener('touchstart', stopAutoplay, { passive: true });
      el.addEventListener('touchend', function () {
        // Resume after a short delay to allow manual scrolling
        setTimeout(resumeAutoplay, 2000);
      }, { passive: true });

      startAutoplay();
    }
  });

  /* ==========================================================
     v4.0 NEW EFFECTS (36-43)
     ========================================================== */

  /* ----------------------------------------------------------
     36. TEXT FILL ON SCROLL (data-animate="text-fill")
     Text starts muted and fills with bright color as user scrolls.
     Uses background-clip:text + GSAP scrub on background-size.
     Inspired by Aceternity/cameronknight's text fill technique.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="text-fill"]').forEach(function (el) {
    var fillColor = el.getAttribute('data-fill-color') || 'var(--color-text, #f3f4f6)';
    var mutedColor = el.getAttribute('data-muted-color') || 'var(--color-text-muted, #3f434a)';
    var delay = parseFloat(el.getAttribute('data-delay') || 0);

    // Wrap text in a span if not already done
    if (!el.querySelector('.text-fill-inner')) {
      var inner = document.createElement('span');
      inner.className = 'text-fill-inner';
      inner.textContent = el.textContent;
      el.textContent = '';
      el.appendChild(inner);
    }

    var target = el.querySelector('.text-fill-inner');
    target.style.cssText = '-webkit-background-clip:text;background-clip:text;color:transparent;display:inline;will-change:background-size;background-color:' + mutedColor + ';background-image:linear-gradient(135deg,' + fillColor + ' 50%,' + mutedColor + ' 60%);background-repeat:no-repeat;background-size:0% 200%;';
    el.style.opacity = '1';

    gsap.to(target, {
      backgroundSize: '200% 200%',
      ease: 'none',
      delay: delay,
      scrollTrigger: {
        trigger: el,
        start: 'top 80%',
        end: 'bottom 35%',
        scrub: true
      }
    });
  });

  /* ----------------------------------------------------------
     37. BORDER BEAM (data-animate="border-beam")
     Animated light beam that travels along card borders.
     Inspired by Magic UI's border-beam component.
     Creates a pseudo-element with conic-gradient that rotates.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="border-beam"]').forEach(function (el) {
    el.style.opacity = '1';
    if (!el.style.position || el.style.position === 'static') {
      el.style.position = 'relative';
    }
    el.style.overflow = 'hidden';

    var beamColor = el.getAttribute('data-beam-color') || 'var(--color-primary, #3b82f6)';
    var beamSize = el.getAttribute('data-beam-size') || '80';
    var speed = parseFloat(el.getAttribute('data-duration') || 4);

    var beam = document.createElement('div');
    beam.className = 'border-beam-el';
    beam.style.cssText = 'position:absolute;inset:-1px;border-radius:inherit;padding:1px;pointer-events:none;z-index:1;overflow:hidden;';

    var inner = document.createElement('div');
    inner.style.cssText = 'position:absolute;inset:0;border-radius:inherit;background:conic-gradient(from 0deg,' + beamColor + ' 0deg,transparent ' + beamSize + 'deg,transparent 360deg);';

    var mask = document.createElement('div');
    mask.style.cssText = 'position:absolute;inset:1px;border-radius:inherit;background:var(--color-bg, #0a0a0a);';

    beam.appendChild(inner);
    beam.appendChild(mask);
    el.appendChild(beam);

    gsap.to(inner, {
      rotation: 360,
      duration: speed,
      ease: 'none',
      repeat: -1,
      transformOrigin: 'center center'
    });
  });

  /* ----------------------------------------------------------
     38. SPOTLIGHT (data-animate="spotlight")
     Mouse-following radial spotlight on section background.
     Creates an ambient premium feel. Desktop only.
     Inspired by Aceternity UI's Spotlight component.
     ---------------------------------------------------------- */
  if (!isMobile) {
    document.querySelectorAll('[data-animate="spotlight"]').forEach(function (el) {
      el.style.opacity = '1';
      if (!el.style.position || el.style.position === 'static') {
        el.style.position = 'relative';
      }
      el.style.overflow = 'hidden';

      var spotColor = el.getAttribute('data-spot-color') || 'rgba(var(--color-primary-rgb, 59,130,246), 0.08)';
      var spotSize = el.getAttribute('data-spot-size') || '600';

      var spot = document.createElement('div');
      spot.className = 'spotlight-el';
      spot.style.cssText = 'position:absolute;width:' + spotSize + 'px;height:' + spotSize + 'px;border-radius:50%;pointer-events:none;z-index:0;opacity:0;transition:opacity 0.5s;background:radial-gradient(circle,' + spotColor + ' 0%,transparent 70%);transform:translate(-50%,-50%);';
      el.appendChild(spot);

      var spotX = gsap.quickTo(spot, 'left', { duration: 0.4, ease: 'power2.out' });
      var spotY = gsap.quickTo(spot, 'top', { duration: 0.4, ease: 'power2.out' });

      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        spotX(e.clientX - rect.left);
        spotY(e.clientY - rect.top);
        spot.style.opacity = '1';
      });
      el.addEventListener('mouseleave', function () {
        spot.style.opacity = '0';
      });
    });
  } else {
    document.querySelectorAll('[data-animate="spotlight"]').forEach(function (el) {
      el.style.opacity = '1';
    });
  }

  /* ----------------------------------------------------------
     39. SHIMMER EFFECT (data-animate="shimmer")
     Diagonal light sweep across element on scroll or continuous.
     Inspired by Magic UI's shimmer button.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="shimmer"]').forEach(function (el) {
    el.style.opacity = '1';
    if (!el.style.position || el.style.position === 'static') {
      el.style.position = 'relative';
    }
    el.style.overflow = 'hidden';

    var shimmer = document.createElement('div');
    shimmer.className = 'shimmer-sweep';
    shimmer.style.cssText = 'position:absolute;top:0;left:-100%;width:60%;height:100%;pointer-events:none;z-index:2;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,0.12) 45%,rgba(255,255,255,0.2) 50%,rgba(255,255,255,0.12) 55%,transparent 60%);';
    el.appendChild(shimmer);

    var continuous = el.getAttribute('data-shimmer-loop') === 'true';
    var speed = parseFloat(el.getAttribute('data-duration') || 2);

    if (continuous) {
      gsap.to(shimmer, {
        left: '200%', duration: speed, ease: 'power1.inOut',
        repeat: -1, repeatDelay: 1.5
      });
    } else {
      gsap.to(shimmer, {
        left: '200%', duration: speed, ease: 'power1.inOut',
        scrollTrigger: { trigger: el, start: 'top 80%', toggleActions: 'play none none none' }
      });
    }
  });

  /* ----------------------------------------------------------
     40. RIPPLE ON CLICK (data-animate="ripple")
     Material Design style click ripple effect.
     Works on buttons, cards, any clickable element.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="ripple"]').forEach(function (el) {
    el.style.opacity = '1';
    if (!el.style.position || el.style.position === 'static') {
      el.style.position = 'relative';
    }
    el.style.overflow = 'hidden';

    var rippleColor = el.getAttribute('data-ripple-color') || 'rgba(255,255,255,0.3)';

    el.addEventListener('click', function (e) {
      var rect = el.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      var maxDim = Math.max(rect.width, rect.height);

      var ripple = document.createElement('span');
      ripple.style.cssText = 'position:absolute;border-radius:50%;pointer-events:none;z-index:5;background:' + rippleColor + ';width:0;height:0;left:' + x + 'px;top:' + y + 'px;transform:translate(-50%,-50%);';
      el.appendChild(ripple);

      gsap.to(ripple, {
        width: maxDim * 2.5, height: maxDim * 2.5, opacity: 0,
        duration: 0.7, ease: 'power2.out',
        onComplete: function () { ripple.remove(); }
      });
    });
  });

  /* ----------------------------------------------------------
     41. INFINITE CARDS (data-animate="infinite-cards")
     Horizontally scrolling card carousel with varied speeds.
     Unlike marquee (for text/logos), this handles card elements
     with individual hover-pause behavior.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="infinite-cards"]').forEach(function (el) {
    el.style.opacity = '1';
    el.style.overflow = 'hidden';

    var track = el.querySelector('.infinite-track');
    if (!track) return;
    var speed = parseFloat(el.getAttribute('data-speed') || 40);
    var dir = el.getAttribute('data-direction') === 'right' ? 1 : -1;
    var pauseOnHover = el.getAttribute('data-pause-hover') !== 'false';

    // Clone items for seamless loop
    var items = track.children;
    var origCount = items.length;
    for (var ci = 0; ci < origCount; ci++) {
      track.appendChild(items[ci].cloneNode(true));
    }

    track.style.display = 'flex';
    track.style.gap = el.getAttribute('data-gap') || '1.5rem';
    track.style.width = 'max-content';

    var totalW = track.scrollWidth / 2;
    var anim = gsap.fromTo(track,
      { x: dir > 0 ? -totalW : 0 },
      { x: dir > 0 ? 0 : -totalW, duration: speed, ease: 'none', repeat: -1 }
    );

    if (pauseOnHover) {
      el.addEventListener('mouseenter', function () { anim.pause(); });
      el.addEventListener('mouseleave', function () { anim.resume(); });
    }
  });

  /* ----------------------------------------------------------
     42. NUMBER TICKER (data-animate="number-ticker")
     Slot-machine style rolling digits counter.
     Each digit rolls independently from 0-9 to its target.
     More visually exciting than the standard counter.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="number-ticker"]').forEach(function (el) {
    var rawTarget = el.getAttribute('data-target') || el.textContent.trim();
    var suffix = el.getAttribute('data-suffix') || '';
    var prefix = el.getAttribute('data-prefix') || '';
    var delay = parseFloat(el.getAttribute('data-delay') || 0);
    var dur = parseFloat(el.getAttribute('data-duration') || 1.5);

    el.innerHTML = '';
    el.style.opacity = '1';
    el.style.display = 'inline-flex';
    el.style.overflow = 'hidden';

    // Add prefix
    if (prefix) {
      var pSpan = document.createElement('span');
      pSpan.textContent = prefix;
      el.appendChild(pSpan);
    }

    // Create digit columns
    var digits = rawTarget.replace(/[^0-9]/g, '').split('');
    var separators = rawTarget.replace(/[0-9]/g, '|').split('|');

    digits.forEach(function (digit, idx) {
      // Add separator before this digit if it exists
      if (separators[idx]) {
        var sep = document.createElement('span');
        sep.textContent = separators[idx];
        el.appendChild(sep);
      }

      var col = document.createElement('span');
      col.style.cssText = 'display:inline-block;overflow:hidden;height:1em;line-height:1;';

      var strip = document.createElement('span');
      strip.style.cssText = 'display:block;';
      for (var d = 0; d <= 9; d++) {
        var numEl = document.createElement('span');
        numEl.textContent = d;
        numEl.style.cssText = 'display:block;height:1em;line-height:1;';
        strip.appendChild(numEl);
      }
      col.appendChild(strip);
      el.appendChild(col);

      var targetDigit = parseInt(digit);
      gsap.fromTo(strip,
        { y: 0 },
        {
          y: -targetDigit + 'em',
          duration: dur + idx * 0.15,
          delay: delay,
          ease: 'power3.out',
          scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' }
        }
      );
    });

    // Add trailing separator + suffix
    if (separators[digits.length]) {
      var trailSep = document.createElement('span');
      trailSep.textContent = separators[digits.length];
      el.appendChild(trailSep);
    }
    if (suffix) {
      var sSpan = document.createElement('span');
      sSpan.textContent = suffix;
      el.appendChild(sSpan);
    }
  });

  /* ----------------------------------------------------------
     43. PARTICLES BACKGROUND (data-animate="particles-bg")
     Lightweight floating particles using canvas.
     No external dependencies — pure Canvas2D.
     Adds depth and motion to hero/CTA sections.
     ---------------------------------------------------------- */
  document.querySelectorAll('[data-animate="particles-bg"]').forEach(function (el) {
    el.style.opacity = '1';
    if (!el.style.position || el.style.position === 'static') {
      el.style.position = 'relative';
    }

    var canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;';
    el.insertBefore(canvas, el.firstChild);

    var ctx = canvas.getContext('2d');
    var particleCount = parseInt(el.getAttribute('data-particle-count') || (isMobile ? 20 : 50));
    var particleColor = el.getAttribute('data-particle-color') || 'var(--color-primary, #3b82f6)';

    // Resolve CSS variable to actual color
    var tempDiv = document.createElement('div');
    tempDiv.style.color = particleColor;
    document.body.appendChild(tempDiv);
    var resolvedColor = getComputedStyle(tempDiv).color;
    document.body.removeChild(tempDiv);

    function resize() {
      var rect = el.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    }
    resize();
    window.addEventListener('resize', resize);

    var particles = [];
    for (var pi = 0; pi < particleCount; pi++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2 + 0.5,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        alpha: Math.random() * 0.5 + 0.1
      });
    }

    var _particleRAF;
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(function (p) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = resolvedColor.replace('rgb(', 'rgba(').replace(')', ',' + p.alpha + ')');
        ctx.fill();
      });

      // Draw connections between nearby particles (desktop only)
      if (!isMobile) {
        for (var a = 0; a < particles.length; a++) {
          for (var b = a + 1; b < particles.length; b++) {
            var dx = particles[a].x - particles[b].x;
            var dy = particles[a].y - particles[b].y;
            var dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 120) {
              ctx.beginPath();
              ctx.moveTo(particles[a].x, particles[a].y);
              ctx.lineTo(particles[b].x, particles[b].y);
              ctx.strokeStyle = resolvedColor.replace('rgb(', 'rgba(').replace(')', ',' + (0.06 * (1 - dist / 120)) + ')');
              ctx.lineWidth = 0.5;
              ctx.stroke();
            }
          }
        }
      }

      _particleRAF = requestAnimationFrame(draw);
    }

    // Only animate when element is visible (performance)
    var particleObserver = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) {
        draw();
      } else {
        cancelAnimationFrame(_particleRAF);
      }
    }, { threshold: 0.1 });
    particleObserver.observe(el);
  });

  /* ==========================================================
     CSS SCROLL-DRIVEN ANIMATIONS — Native Layer
     Progressive enhancement: adds CSS-native scroll animations
     for browsers that support them (Chrome 115+).
     These run on the compositor thread = zero JS overhead.
     ========================================================== */
  (function injectNativeScrollCSS() {
    if (!CSS.supports || !CSS.supports('animation-timeline', 'view()')) return;

    var nativeCSS = document.createElement('style');
    nativeCSS.textContent = [
      '/* Native CSS Scroll-Driven Animations (v4.0) */',
      '@supports (animation-timeline: view()) {',
      '  /* Fade-up native for elements with data-native-scroll */',
      '  [data-native-scroll="fade-up"] {',
      '    animation: nativeFadeUp linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 10% cover 40%;',
      '  }',
      '  @keyframes nativeFadeUp {',
      '    from { opacity: 0; transform: translateY(40px); }',
      '    to { opacity: 1; transform: translateY(0); }',
      '  }',
      '',
      '  /* Scale-in native */',
      '  [data-native-scroll="scale-in"] {',
      '    animation: nativeScaleIn linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 10% cover 35%;',
      '  }',
      '  @keyframes nativeScaleIn {',
      '    from { opacity: 0; transform: scale(0.85); }',
      '    to { opacity: 1; transform: scale(1); }',
      '  }',
      '',
      '  /* Blur-in native */',
      '  [data-native-scroll="blur-in"] {',
      '    animation: nativeBlurIn linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 5% cover 35%;',
      '  }',
      '  @keyframes nativeBlurIn {',
      '    from { opacity: 0; filter: blur(12px); transform: translateY(20px); }',
      '    to { opacity: 1; filter: blur(0px); transform: translateY(0); }',
      '  }',
      '',
      '  /* Reveal-up native (clip-path) */',
      '  [data-native-scroll="reveal-up"] {',
      '    animation: nativeRevealUp linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 10% cover 40%;',
      '  }',
      '  @keyframes nativeRevealUp {',
      '    from { clip-path: inset(100% 0 0 0); }',
      '    to { clip-path: inset(0 0 0 0); }',
      '  }',
      '',
      '  /* Slide-left native */',
      '  [data-native-scroll="slide-left"] {',
      '    animation: nativeSlideLeft linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 10% cover 40%;',
      '  }',
      '  @keyframes nativeSlideLeft {',
      '    from { opacity: 0; transform: translateX(60px); }',
      '    to { opacity: 1; transform: translateX(0); }',
      '  }',
      '',
      '  /* Slide-right native */',
      '  [data-native-scroll="slide-right"] {',
      '    animation: nativeSlideRight linear both;',
      '    animation-timeline: view();',
      '    animation-range: entry 10% cover 40%;',
      '  }',
      '  @keyframes nativeSlideRight {',
      '    from { opacity: 0; transform: translateX(-60px); }',
      '    to { opacity: 1; transform: translateX(0); }',
      '  }',
      '',
      '  /* Scroll progress indicator (native) */',
      '  [data-native-scroll="progress"] {',
      '    animation: nativeProgress linear;',
      '    animation-timeline: scroll(root);',
      '    transform-origin: left;',
      '  }',
      '  @keyframes nativeProgress {',
      '    from { transform: scaleX(0); }',
      '    to { transform: scaleX(1); }',
      '  }',
      '}'
    ].join('\n');
    document.head.appendChild(nativeCSS);
  })();

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
