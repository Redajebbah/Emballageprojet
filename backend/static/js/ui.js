// UI interactions for Emboitage
// - header shadow on scroll
// - mobile drawer menu
// - product gallery thumbnails
// - size chips (update price + WhatsApp message)
// - WhatsApp quote form
// - reveal-on-scroll animations

(function () {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Header: subtle border/shadow once the page is scrolled
  function initHeader() {
    const header = $('#siteHeader');
    if (!header) return;
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Mobile drawer
  function initDrawer() {
    const drawer = $('#drawer');
    const openBtn = $('[data-drawer-open]');
    if (!drawer || !openBtn) return;

    const setOpen = (open) => {
      document.body.classList.toggle('drawer-open', open);
      drawer.setAttribute('aria-hidden', String(!open));
      openBtn.setAttribute('aria-expanded', String(open));
      if (open) $('input', drawer)?.focus({ preventScroll: true });
      else openBtn.focus({ preventScroll: true });
    };

    openBtn.addEventListener('click', () => setOpen(true));
    $$('[data-drawer-close]').forEach((el) => el.addEventListener('click', () => setOpen(false)));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.body.classList.contains('drawer-open')) setOpen(false);
    });
  }

  // Product gallery: swap main image when clicking a thumbnail
  function initGallery() {
    const main = $('#galleryMain');
    const thumbs = $$('.gallery-thumbs button');
    if (!main || !thumbs.length) return;
    thumbs.forEach((btn) => {
      btn.addEventListener('click', () => {
        main.src = btn.dataset.src;
        thumbs.forEach((b) => b.classList.toggle('is-active', b === btn));
      });
    });
  }

  // Size chips: show the size price and add the size to the WhatsApp message
  function initSizes() {
    const chips = $$('.size-chip');
    if (!chips.length) return;
    const priceEls = $$('[data-price-display]');
    const hint = $('[data-size-hint]');
    const waLinks = $$('[data-wa-link]');
    const baseTexts = waLinks.map((a) => new URL(a.href).searchParams.get('text') || '');
    const fmt = (v) => Number(v).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    chips.forEach((chip) => {
      chip.addEventListener('click', () => {
        chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
        const { sizeLabel, sizePrice } = chip.dataset;
        priceEls.forEach((el) => { el.innerHTML = `${fmt(sizePrice)}<small>MAD</small>`; });
        if (hint) hint.textContent = sizeLabel;
        waLinks.forEach((a, i) => {
          const url = new URL(a.href);
          url.searchParams.set('text', `${baseTexts[i]}\nTaille : ${sizeLabel} (${fmt(sizePrice)} MAD)`);
          a.href = url.toString();
        });
      });
    });
  }

  // Contact form: open WhatsApp with the message pre-filled
  function initWhatsAppForm() {
    $$('[data-wa-form]').forEach((form) => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!form.reportValidity()) return;
        const data = new FormData(form);
        const lines = [
          'Bonjour Emboitage, je souhaite un devis.',
          `Nom / Société : ${data.get('name')}`,
          data.get('city') ? `Ville : ${data.get('city')}` : null,
          `Besoin : ${data.get('message')}`,
        ].filter(Boolean);
        const url = `https://wa.me/${form.dataset.waNumber}?text=${encodeURIComponent(lines.join('\n'))}`;
        window.open(url, '_blank', 'noopener');
      });
    });
  }

  // Reveal elements as they enter the viewport
  function initReveal() {
    const items = $$('.reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) {
      items.forEach((el) => el.classList.add('is-visible'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach((el, i) => {
      el.style.transitionDelay = `${Math.min(i % 4, 3) * 70}ms`;
      io.observe(el);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initHeader();
    initDrawer();
    initGallery();
    initSizes();
    initWhatsAppForm();
    initReveal();
  });
})();
