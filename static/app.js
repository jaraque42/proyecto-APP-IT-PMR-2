// Agregar prefijo 34 a teléfono
function addPhonePrefix(input) {
  if (!input.value) return;
  let val = input.value.toString().trim();
  if (!val.startsWith('34')) {
    val = '34' + val.replace(/^0+/, '');
    input.value = val;
  }
}

// Validación ligera y UX mínima
document.addEventListener('submit', function(e){
  const form = e.target;
  if(form.tagName.toLowerCase() !== 'form') return;
  const imei = form.querySelector('[name=imei]');
  const usuario = form.querySelector('[name=usuario]');
  const telefono = form.querySelector('[name=telefono]');
  
  if(imei && imei.value.trim()===''){
    e.preventDefault();
    alert('IMEI es requerido');
    imei.focus();
    return;
  }
  if(usuario && usuario.value.trim()===''){
    e.preventDefault();
    alert('Usuario es requerido');
    usuario.focus();
    return;
  }
  if(telefono && telefono.value.trim()!==''){
    addPhonePrefix(telefono);
  }
});

// Agregar prefijo al salir del campo de teléfono
document.querySelectorAll('[name=telefono]').forEach(function(input){
  input.addEventListener('blur', function(){
    if(this.value.trim()!==''){
      addPhonePrefix(this);
    }
  });
});

// Tabla de histórico: seleccionar todo, exportar y botones
document.addEventListener('DOMContentLoaded', function(){
  // Select all checkbox de la tabla
  const selectAllCheckbox = document.getElementById('select-all');
  if(selectAllCheckbox){
    selectAllCheckbox.addEventListener('change', function(){
      const checked = this.checked;
      document.querySelectorAll('.row-select').forEach(function(cb){ cb.checked = checked; });
    });
  }

  // Botón "Seleccionar todo"
  const selectAllBtn = document.getElementById('select-all-rows');
  if(selectAllBtn){
    selectAllBtn.addEventListener('click', function(e){
      e.preventDefault();
      document.querySelectorAll('.row-select').forEach(function(cb){ cb.checked = true; });
      if(selectAllCheckbox) selectAllCheckbox.checked = true;
    });
  }
  
  // Botón "Deseleccionar"
  const deselectAllBtn = document.getElementById('deselect-all-rows');
  if(deselectAllBtn){
    deselectAllBtn.addEventListener('click', function(e){
      e.preventDefault();
      document.querySelectorAll('.row-select').forEach(function(cb){ cb.checked = false; });
      if(selectAllCheckbox) selectAllCheckbox.checked = false;
    });
  }

  // Botón "Exportar solo seleccionados"
  const exportBtn = document.getElementById('export-selected-btn');
  if(exportBtn){
    exportBtn.addEventListener('click', function(e){
      e.preventDefault();
      const checkboxes = document.querySelectorAll('.row-select');
      const ids = [];
      checkboxes.forEach(function(cb){
        if(cb.checked){
          ids.push(cb.value);
        }
      });
      
      // Si NO hay seleccionados, mostrar alerta
      if(ids.length === 0){
        alert('Selecciona al menos un registro para exportar.');
        return;
      }
      
      // Exportar solo los seleccionados
      const params = new URLSearchParams();
      params.set('ids', ids.join(','));
       // Detectar si estamos en /incidents o /history
       const exportUrl = window.location.pathname.includes('/incidents') ? '/incidents/export' : '/history/export';
       window.location.href = exportUrl + '?' + params.toString();
    });
  }

  // Botón "Borrar seleccionados"
  const deleteBtn = document.getElementById('delete-selected-btn');
  if(deleteBtn){
    deleteBtn.addEventListener('click', function(e){
      e.preventDefault();
      const checkboxes = document.querySelectorAll('.row-select');
      const ids = [];
      checkboxes.forEach(function(cb){
        if(cb.checked){
          ids.push(cb.value);
        }
      });
      
      // Si NO hay seleccionados, mostrar alerta
      if(ids.length === 0){
        alert('Selecciona al menos un registro para borrar.');
        return;
      }
      
      // Pedir confirmación y contraseña
      if(!confirm('¿Está seguro de que desea borrar los registros seleccionados? Esta acción no se puede deshacer.')){
        return;
      }
      
      const password = prompt('Introduce la contraseña para borrar:');
      if(!password){
        return;
      }
      
      // Crear y enviar formulario POST
      const form = document.createElement('form');
      form.method = 'POST';
       // Detectar si estamos en /incidents o /history
       const deleteUrl = window.location.pathname.includes('/incidents') ? '/incidents/delete-selected' : '/history/delete-selected';
       form.action = deleteUrl;
      
      const idsInput = document.createElement('input');
      idsInput.type = 'hidden';
      idsInput.name = 'ids';
      idsInput.value = ids.join(',');
      form.appendChild(idsInput);
      
      const passInput = document.createElement('input');
      passInput.type = 'hidden';
      passInput.name = 'password';
      passInput.value = password;
      form.appendChild(passInput);
      
      document.body.appendChild(form);
      form.submit();
    });
  }

  // Botón "Borrar Histórico" (borrar todo)
  const clearHistoryBtn = document.getElementById('clear-history-btn');
  if(clearHistoryBtn){
    clearHistoryBtn.addEventListener('click', function(e){
      e.preventDefault();
      
      // Pedir confirmación
      if(!confirm('¿Está seguro de que desea borrar TODO el histórico? Esta acción no se puede deshacer.')){
        return;
      }
      
      const password = prompt('Introduce la contraseña para borrar TODO el histórico:');
      if(!password){
        return;
      }
      
      // Crear y enviar formulario POST
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/history/clear';
      
      const passInput = document.createElement('input');
      passInput.type = 'hidden';
      passInput.name = 'password';
      passInput.value = password;
      form.appendChild(passInput);
      
      document.body.appendChild(form);
      form.submit();
    });
  }

  // --- Toast notifications ---
  function createToast(message, category){
    const container = document.getElementById('toast-container');
    if(!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast ' + (category === 'error' ? 'error' : (category === 'success' ? 'success' : 'info'));

    const msg = document.createElement('span');
    msg.className = 'message';
    msg.textContent = message;
    toast.appendChild(msg);

    const close = document.createElement('button');
    close.className = 'close';
    close.innerHTML = '✕';
    close.addEventListener('click', function(){
      hideToast(toast);
    });
    toast.appendChild(close);

    container.appendChild(toast);

    // Force reflow then show
    setTimeout(function(){ toast.classList.add('show'); }, 20);

    // Auto hide
    const timeout = setTimeout(function(){ hideToast(toast); }, 5000);

    // Keep reference to timeout in dataset for manual close
    toast.dataset.timeoutId = timeout;
  }

  function hideToast(toast){
    if(!toast) return;
    const timeoutId = toast.dataset.timeoutId;
    if(timeoutId) clearTimeout(timeoutId);
    toast.classList.remove('show');
    setTimeout(function(){ try{ toast.remove(); }catch(e){} }, 300);
  }

  // Si hay mensajes pasados por el servidor, mostrarlos como toasts
  if(window.server_messages && Array.isArray(window.server_messages)){
    window.server_messages.forEach(function(pair){
      const category = pair[0];
      const message = pair[1];
      createToast(message, category);
    });
    // Limpiar para que no reaparezcan si se hace pushState o similar
    window.server_messages = null;
  }

  // --- Dark mode toggle ---
  function applyDarkMode(isDark) {
    if(isDark) document.body.classList.add('dark'); else document.body.classList.remove('dark');
    const btn = document.getElementById('dark-mode-toggle');
    if(!btn) return;
    btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    btn.title = isDark ? 'Activar modo claro' : 'Activar modo oscuro';
    btn.classList.toggle('light', !isDark);
    btn.innerHTML = isDark ? '☀' : '🌙';
  }

  // Crear botón si no existe
  let dmBtn = document.getElementById('dark-mode-toggle');
  if(!dmBtn){
    dmBtn = document.createElement('button');
    dmBtn.id = 'dark-mode-toggle';
    dmBtn.type = 'button';
    dmBtn.setAttribute('aria-label', 'Modo oscuro');
    document.body.appendChild(dmBtn);
  }

  // Inicializar estado desde localStorage
  const storedDark = localStorage.getItem('darkMode') === 'true';
  applyDarkMode(storedDark);

  dmBtn.addEventListener('click', function(){
    const isDarkNow = !document.body.classList.contains('dark');
    localStorage.setItem('darkMode', isDarkNow);
    applyDarkMode(isDarkNow);
  });

});
