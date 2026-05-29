/**
 * overflow-detect-plugin.js — Bespoke.js plugin
 *
 * Auto-detects content overflow on Marp slides and applies CSS classes
 * overflow-1 … overflow-68 (pixel-by-pixel severity, cividis colormap).
 * Also collapses top padding to 60px when a slide has no H1.
 *
 * Usage with Marp CLI:
 *   marp --bespoke.overflow-detect=./scripts/overflow-detect-plugin.js slides.md
 *
 * Or as an HTML snippet (inline version):
 *   see the companion snippet at the end of this file.
 */

(function () {
  'use strict';

  var MAX = 68;
  var ro = null;

  function updateSlide(slide) {
    // ---- H1 auto-padding ----
    if (!slide.querySelector('h1')) {
      slide.style.paddingTop = '60px';
    }

    // ---- overflow-N classes ----
    // Remove any previously set overflow-N classes
    slide.classList.forEach(function (cls) {
      if (/^overflow-\d+$/.test(cls)) {
        slide.classList.remove(cls);
      }
    });

    // Respect explicit hide
    if (slide.classList.contains('overflow-hidden')) return;

    // Always clean up overflow-active if JS is managing detection;
    // but leave it if the user set it manually (we can't easily
    // distinguish, so removing it is the safer default).
    slide.classList.remove('overflow-active');

    var overflow = slide.scrollHeight - slide.clientHeight;
    if (overflow > 0) {
      var level = Math.min(Math.ceil(overflow), MAX);
      slide.classList.add('overflow-' + level);
    }
  }

  function scanAll(deck) {
    var slides = deck ? deck.slides : document.querySelectorAll('section');
    for (var i = 0; i < slides.length; i++) {
      updateSlide(slides[i]);
    }
  }

  // ---- Bespoke plugin factory ----
  module.exports = function overflowDetectPlugin() {
    return function (deck) {
      // Observe all slides with ResizeObserver
      if (typeof ResizeObserver !== 'undefined') {
        ro = new ResizeObserver(function () {
          scanAll(deck);
        });
        for (var i = 0; i < deck.slides.length; i++) {
          ro.observe(deck.slides[i]);
        }
      }

      // Re-check after slide transitions (bespoke fires 'activate')
      deck.on('activate', function () {
        setTimeout(function () {
          scanAll(deck);
        }, 50);
      });

      // Initial scan — wait for fonts & Marp auto-scaling to settle
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(function () {
          setTimeout(function () {
            scanAll(deck);
          }, 150);
        });
      } else {
        setTimeout(function () {
          scanAll(deck);
        }, 300);
      }
    };
  };

})();

/* ================================================================
   INLINE HTML SNIPPET (paste into Markdown to use without CLI)
   ================================================================

<script>
(function(){const M=68;var r;function u(s){if(!s.querySelector("h1"))s.style.paddingTop="60px";s.classList.forEach(c=>{if(/^overflow-\d+$/.test(c))s.classList.remove(c)});if(s.classList.contains("overflow-hidden"))return;s.classList.remove("overflow-active");const o=s.scrollHeight-s.clientHeight;if(o>0)s.classList.add("overflow-"+Math.min(Math.ceil(o),M));}function a(d){Array.from(d||document.querySelectorAll("section")).forEach(u);}document.fonts.ready.then(()=>{a();if("ResizeObserver"in window){r=new ResizeObserver(()=>a());document.querySelectorAll("section").forEach(s=>r.observe(s));}});})();
</script>

*/
