/* GSAP Universal Animations - Auto-injected in every generated site */
document.addEventListener('DOMContentLoaded', function() {
  gsap.registerPlugin(ScrollTrigger);

  // Animation configs mapped to data-animate values
  var animations = {
    'fade-up':    { y: 40, opacity: 0 },
    'fade-down':  { y: -40, opacity: 0 },
    'fade-left':  { x: -60, opacity: 0 },
    'fade-right': { x: 60, opacity: 0 },
    'scale-in':   { scale: 0.85, opacity: 0 },
    'reveal':     { clipPath: 'inset(0 100% 0 0)', opacity: 0 }
  };

  // Animate all elements with data-animate attribute
  document.querySelectorAll('[data-animate]').forEach(function(el) {
    var type = el.getAttribute('data-animate');
    var config = animations[type];
    if (!config) { el.style.opacity = 1; return; }

    var fromVars = Object.assign({}, config);
    var toVars = {
      y: 0, x: 0, scale: 1, opacity: 1,
      clipPath: 'inset(0 0% 0 0)',
      duration: 0.8,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        toggleActions: 'play none none none'
      }
    };

    gsap.fromTo(el, fromVars, toVars);
  });

  // Stagger animation for repeated items
  document.querySelectorAll('[data-animate="stagger"]').forEach(function(container) {
    var items = container.querySelectorAll('.stagger-item');
    if (items.length === 0) return;

    gsap.fromTo(items,
      { y: 30, opacity: 0 },
      {
        y: 0, opacity: 1,
        duration: 0.6,
        stagger: 0.15,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: container,
          start: 'top 85%',
          toggleActions: 'play none none none'
        }
      }
    );
  });

  // Counter animation for elements with data-counter
  document.querySelectorAll('[data-counter]').forEach(function(el) {
    var target = parseInt(el.getAttribute('data-counter'), 10);
    var suffix = el.getAttribute('data-counter-suffix') || '';
    var obj = { val: 0 };

    gsap.to(obj, {
      val: target,
      duration: 2,
      ease: 'power1.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        toggleActions: 'play none none none'
      },
      onUpdate: function() {
        el.textContent = Math.round(obj.val) + suffix;
      }
    });
  });

  // Hamburger menu toggle
  var menuBtn = document.getElementById('menu-toggle');
  var mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', function() {
      mobileMenu.classList.toggle('hidden');
      var isOpen = !mobileMenu.classList.contains('hidden');
      menuBtn.setAttribute('aria-expanded', isOpen);
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Close mobile menu if open
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
          mobileMenu.classList.add('hidden');
        }
      }
    });
  });
});
