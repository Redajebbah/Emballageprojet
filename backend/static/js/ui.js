// UI micro-interactions for Emballage
// - mobile nav toggle
// - add-to-cart ajax enhancement
// - simple toast notifications
// - cart page dynamic subtotal / total recalculation

(function(){
  'use strict';

  // Helpers
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));

  // Toast system
  function createToastArea(){
    if ($('#eb-toast-area')) return;
    const area = document.createElement('div');
    area.id = 'eb-toast-area';
    Object.assign(area.style,{position:'fixed', right:'18px', bottom:'18px', zIndex:1000});
    document.body.appendChild(area);
  }

  function showToast(message, type='info', duration=2200){
    createToastArea();
    const t = document.createElement('div');
    t.className = 'eb-toast eb-toast-'+type;
    t.textContent = message;
    t.style.cssText = 'background:#fff;border-radius:10px;padding:10px 14px;margin-top:8px;box-shadow:0 12px 28px rgba(16,24,40,0.08);border:1px solid rgba(16,24,40,0.04);min-width:160px;font-weight:600;color:#1f2937';
    $('#eb-toast-area').appendChild(t);
    setTimeout(()=>{ t.style.transition='opacity .25s ease'; t.style.opacity=0; setTimeout(()=>t.remove(),300); }, duration);
  }

  // CSRF helper
  function getCookie(name) {
    if (!document.cookie) return null;
    const csrfMatch = document.cookie.split(';').map(c => c.trim()).filter(c => c.startsWith(name+'='))[0];
    if (!csrfMatch) return null;
    return decodeURIComponent(csrfMatch.split('=')[1]);
  }

  // Intercept add-to-cart forms to provide AJAX feedback & update header count
  function initAddToCartAjax(){
    document.addEventListener('submit', function(e){
      const form = e.target;
      if (form && form.matches && form.matches('form[action][method][action*="cart/add"]')){
        // allow normal post if JS unavailable; use JS to enhance
        e.preventDefault();
        const data = new FormData(form);
        const action = form.getAttribute('action');
        const csrftoken = getCookie('csrftoken');
        fetch(action, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrftoken },
          body: data,
        }).then(resp => {
          // success redirect -> cart page usually, but for UX we show toast and update count
          if (resp.ok || resp.status === 302 || resp.status === 200){
            // increment visual cart count if present
            const cartCountEl = document.querySelector('.nav-actions a[href*="/cart/"] span');
            if (cartCountEl){
              let cur = parseInt(cartCountEl.textContent.replace(/[()]/g,'')) || 0;
              const qty = parseInt(data.get('quantity') || 1) || 1;
              cartCountEl.textContent = '(' + (cur+qty) + ')';
            }
            showToast('Produit ajouté au panier ✅');
          } else {
            showToast('Erreur lors de l\'ajout au panier', 'error');
          }
        }).catch(err => { showToast('Erreur réseau', 'error'); console.error(err); });
      }
    }, true);
  }

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

  // Cart page client-side subtotals and total recalculation
  function initCartDynamicTotals(){
    const cartTable = document.querySelector('.cart-table');
    if (!cartTable) return;
    function recalc(){
      let total = 0; // Decimal precision not perfect, acceptable for display
      document.querySelectorAll('.cart-table tbody tr').forEach(row=>{
        const qtyInput = row.querySelector('input[type="number"][name="quantity"]');
        const priceText = row.querySelector('td:nth-child(2)').textContent.trim();
        const price = parseFloat(priceText.replace(/[DH ,]+/g, '')) || 0;
        const qty = parseInt(qtyInput.value) || 0;
        const subtotal = price * qty;
        const subcell = row.querySelector('td:nth-child(4)');
        if (subcell) subcell.textContent = subtotal.toFixed(2) + ' DH';
        total += subtotal;
      });
      const totalEl = document.querySelector('.d-flex.justify-content-between .h4') || document.querySelector('.h4');
      if (totalEl) totalEl.textContent = total.toFixed(2) + ' DH';
    }
    // attach listener to quantity inputs
    cartTable.addEventListener('input', function(e){ if (e.target && e.target.matches('input[type="number"][name="quantity"]')){ recalc(); }});
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
    initAddToCartAjax();
    initMobileNav();
    initSearchSuggestions();
    initCartDynamicTotals();
    initDetailThumbnails();
  });
})();
