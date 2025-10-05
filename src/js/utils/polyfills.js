// Polyfills for older browsers
(function() {
  'use strict';

  // Custom element polyfill for older browsers
  if (!window.customElements) {
    console.warn('Custom Elements not supported, some features may not work');
  }

  // Promise.allSettled polyfill
  if (!Promise.allSettled) {
    Promise.allSettled = function(promises) {
      return Promise.all(
        promises.map(p => Promise.resolve(p).then(
          value => ({ status: 'fulfilled', value }),
          reason => ({ status: 'rejected', reason })
        ))
      );
    };
  }

  // AbortController polyfill for older browsers
  if (!window.AbortController) {
    window.AbortController = class AbortController {
      constructor() {
        this.signal = { aborted: false };
      }
      abort() {
        this.signal.aborted = true;
      }
    };
  }

  // Object.fromEntries polyfill
  if (!Object.fromEntries) {
    Object.fromEntries = function(entries) {
      const obj = {};
      for (const [key, value] of entries) {
        obj[key] = value;
      }
      return obj;
    };
  }

  // String.prototype.replaceAll polyfill
  if (!String.prototype.replaceAll) {
    String.prototype.replaceAll = function(search, replace) {
      return this.split(search).join(replace);
    };
  }

  // Array.prototype.at polyfill
  if (!Array.prototype.at) {
    Array.prototype.at = function(index) {
      const len = this.length;
      const relativeIndex = index < 0 ? len + index : index;
      if (relativeIndex < 0 || relativeIndex >= len) {
        return undefined;
      }
      return this[relativeIndex];
    };
  }

  // Intersection Observer polyfill check
  if (!('IntersectionObserver' in window)) {
    console.warn('IntersectionObserver not supported, lazy loading may not work');
  }

  // CSS.supports polyfill
  if (!window.CSS || !window.CSS.supports) {
    window.CSS = window.CSS || {};
    window.CSS.supports = function() {
      return false; // Conservative fallback
    };
  }

  // Console polyfill for very old browsers
  if (!window.console) {
    window.console = {
      log: function() {},
      error: function() {},
      warn: function() {},
      info: function() {},
      debug: function() {}
    };
  }

  // RequestAnimationFrame polyfill
  if (!window.requestAnimationFrame) {
    window.requestAnimationFrame = function(callback) {
      return setTimeout(callback, 16);
    };
    window.cancelAnimationFrame = function(id) {
      clearTimeout(id);
    };
  }

  // Modern event methods polyfill
  if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                Element.prototype.webkitMatchesSelector;
  }

  if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
      var el = this;
      do {
        if (Element.prototype.matches.call(el, s)) return el;
        el = el.parentElement || el.parentNode;
      } while (el !== null && el.nodeType === 1);
      return null;
    };
  }

  // Performance.now polyfill
  if (!window.performance || !window.performance.now) {
    window.performance = window.performance || {};
    window.performance.now = function() {
      return Date.now();
    };
  }

  // URL constructor polyfill check
  try {
    new URL('http://example.com');
  } catch (e) {
    console.warn('URL constructor not supported, some URL parsing may fail');
  }

  // Fetch polyfill check (but don't implement - it's complex)
  if (!window.fetch) {
    console.error('Fetch API not supported. Please include a fetch polyfill or use a modern browser.');
  }

  // Check for ES6 features and warn if missing
  try {
    eval('const x = () => {}');
  } catch (e) {
    console.error('ES6 features not supported. Please use a modern browser or include a transpiler.');
  }
})();