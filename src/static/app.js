// UX helpers: keyboard shortcuts + copy buttons + toast
(function(){
  const toast = (msg) => {
    let el = document.querySelector('.toast');
    if(!el){
      el = document.createElement('div');
      el.className = 'toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(window.__toast_t);
    window.__toast_t = setTimeout(()=> el.classList.remove('show'), 1800);
  };

  // Copy buttons (result page)
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-copy]');
    if(!btn) return;
    const id = btn.getAttribute('data-copy');
    const pre = document.querySelector(id);
    if(!pre) return;
    try{
      await navigator.clipboard.writeText(pre.textContent.trim());
      toast('✅ Copiado al portapapeles');
      const prev = btn.textContent;
      btn.textContent = 'Copiado ✅';
      btn.disabled = true;
      setTimeout(()=>{ btn.textContent = prev; btn.disabled = false; }, 1100);
    }catch(err){
      // fallback
      const t = document.createElement('textarea');
      t.value = pre.textContent.trim();
      document.body.appendChild(t);
      t.select();
      document.execCommand('copy');
      t.remove();
      toast('✅ Copiado (modo compatibilidad)');
      const prev = btn.textContent;
      btn.textContent = 'Copiado ✅';
      btn.disabled = true;
      setTimeout(()=>{ btn.textContent = prev; btn.disabled = false; }, 1100);
    }
  });

  // Activation simulation (result page)
  const actBtn = document.getElementById('activateBtn');
  if(actBtn){
    actBtn.addEventListener('click', () => {
      if(actBtn.classList.contains('activated')) return;
      actBtn.textContent = 'Plan activado ✅';
      actBtn.disabled = true;
      actBtn.classList.add('activated');
      toast('✅ Plan activado (simulación)');
    });
  }

  // Ctrl+Enter submits the form (index page)
  const form = document.querySelector('form[action="/recomendar"]');
  if(form){
    document.addEventListener('keydown', (e) => {
      if((e.ctrlKey || e.metaKey) && e.key === 'Enter'){
        e.preventDefault();
        form.requestSubmit();
      }
    });
  }
})();

// smooth scroll for in-page anchors (tabs)
document.addEventListener('click', (e) => {
  const a = e.target.closest('a.tab[href^="#"]');
  if(!a) return;
  e.preventDefault();
  const id = a.getAttribute('href');
  const el = document.querySelector(id);
  if(el){
    el.scrollIntoView({behavior: 'smooth', block: 'start'});
    history.replaceState(null, '', id);
  }
});
