// UI micro-interactions for Emballage
// - mobile nav toggle
// - search suggestions
// - product detail thumbnails

(function(){
  'use strict';

  // Helpers
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));

  // Mobile nav toggle - Smooth animated dropdown menu
  function initMobileNav(){
    const toggle = document.getElementById('mobileMenuToggle');
    const menu = document.getElementById('mobileMenu');
    
    if (!toggle || !menu) return;
    
    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      
      // Toggle active states
      toggle.classList.toggle('active');
      menu.classList.toggle('active');
      
      // Close menu when clicking outside
      if (menu.classList.contains('active')) {
        setTimeout(() => {
          document.addEventListener('click', closeMenuOnClickOutside);
        }, 100);
      } else {
        document.removeEventListener('click', closeMenuOnClickOutside);
      }
    });
    
    function closeMenuOnClickOutside(e) {
      if (!menu.contains(e.target) && !toggle.contains(e.target)) {
        toggle.classList.remove('active');
        menu.classList.remove('active');
        document.removeEventListener('click', closeMenuOnClickOutside);
      }
    }
    
    // Close menu when a link is clicked
    menu.querySelectorAll('.mobile-menu-item').forEach(item => {
      item.addEventListener('click', function() {
        toggle.classList.remove('active');
        menu.classList.remove('active');
        document.removeEventListener('click', closeMenuOnClickOutside);
      });
    });
    
    // Close menu on ESC key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && menu.classList.contains('active')) {
        toggle.classList.remove('active');
        menu.classList.remove('active');
        document.removeEventListener('click', closeMenuOnClickOutside);
      }
    });
  }

  // Tiny search suggestions using product titles visible on page
  function initSearchSuggestions(){
    const search = document.querySelector('input[name="q"]');
    if (!search) return;
    const pool = Array.from(document.querySelectorAll('.product-title')).map(n=>n.textContent.trim()).filter(Boolean);
    const list = document.createElement('div'); list.className='eb-search-suggestions'; list.style.cssText='position:absolute; background:var(--white); border-radius:8px; box-shadow:var(--shadow-subtle); width:100%; z-index:99; display:none;';
    search.parentNode.style.position='relative'; search.parentNode.appendChild(list);
    search.addEventListener('input', ()=>{
      const val = search.value.toLowerCase().trim();
      if (!val){ list.style.display='none'; return; }
      const matches = pool.filter(t=> t.toLowerCase().includes(val)).slice(0,6);
      list.innerHTML = matches.map(m=>`<div class=\"px-3 py-2 eb-sug\">${m}</div>`).join('') + (matches.length? '<div class="px-3 py-2 text-muted small">Appuyez Entrée pour rechercher</div>':'');
      list.style.display = matches.length? 'block':'none';
    });
    list.addEventListener('click',(ev)=>{ if (ev.target.matches('.eb-sug')){ search.value = ev.target.textContent; search.form && search.form.submit(); } });
  }

  // Product detail thumbnails: swap main image when clicking thumbnails
  function initDetailThumbnails(){
    const main = document.getElementById('main-product-image');
    if (!main) return;
    document.querySelectorAll('.detail-image img.img-thumbnail').forEach(t => {
      t.addEventListener('click', ()=>{
        const src = t.getAttribute('data-src') || t.src;
        if (src){
          main.src = src;
          // highlight briefly
          main.style.transition = 'transform .18s ease'; main.style.transform='scale(0.995)';
          setTimeout(()=> main.style.transform='scale(1)', 180);
        }
      });
    });
  }

  // Initialize all
  document.addEventListener('DOMContentLoaded', function(){
    initMobileNav();
    initSearchSuggestions();
    initDetailThumbnails();
  });
})();