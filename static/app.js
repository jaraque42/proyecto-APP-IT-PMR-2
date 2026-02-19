// Nota: se eliminó el prefijado automático '34' por petición del usuario.
// La normalización/validación se realiza en el servidor.

// Función global para manejar borrado con contraseña admin
window.confirmAdminDelete = function(event, message) {
  if (!confirm(message)) {
    event.preventDefault();
    return false;
  }
  const password = prompt("Introduce la contraseña de ADMIN para confirmar:");
  if (!password) {
    event.preventDefault();
    return false;
  }
  
  const form = event.target;
  let passInput = form.querySelector('input[name="admin_password"]');
  if (!passInput) {
    passInput = document.createElement('input');
    passInput.type = 'hidden';
    passInput.name = 'admin_password';
    form.appendChild(passInput);
  }
  passInput.value = password;
  return true;
};

// Validación ligera y UX mínima
document.addEventListener('submit', function(e){
  const form = e.target;
  if(form.tagName.toLowerCase() !== 'form') return;

  // No validar formularios de búsqueda (method GET) — permiten búsquedas parciales
  if(form.method.toLowerCase() === 'get') return;

  const imei = form.querySelector('[name=imei]');
  const usuario = form.querySelector('[name=usuario]');
  const telefono = form.querySelector('[name=telefono]');
  
  // Validación avanzada basada en atributos pattern / minlength / maxlength
  function removeFieldError(input){
    input.classList.remove('input-error');
    try{ input.setCustomValidity(''); }catch(e){}
    const next = input.nextElementSibling;
    if(next && next.classList && next.classList.contains('field-error-message')) next.remove();
  }

  function showInvalid(input, message){
    // non-blocking inline error under the field
    removeFieldError(input);
    input.classList.add('input-error');
    const msg = document.createElement('div');
    msg.className = 'field-error-message';
    msg.textContent = message;
    input.insertAdjacentElement('afterend', msg);
    try{ input.setCustomValidity(message); }catch(e){}
    input.focus();
  }

  if(imei){
    const v = imei.value.trim();
    const pat = imei.getAttribute('pattern');
    if(imei.hasAttribute('required') && v===''){
      e.preventDefault(); showInvalid(imei, 'IMEI es requerido'); return;
    }
    if(v!=='' && pat){
      const re = new RegExp('^'+pat+'$');
      if(!re.test(v)){
        e.preventDefault(); showInvalid(imei, 'IMEI inválido — debe tener 15 dígitos'); return;
      }
    }
  }

  // Ensure IMEI is exactly 15 digits (ignore non-digits)
  if(imei){
    const digits = (imei.value || '').replace(/\D/g, '');
    if(digits.length > 0 && digits.length !== 15){
      e.preventDefault(); showInvalid(imei, 'IMEI inválido — debe contener exactamente 15 dígitos'); return;
    }
  }

  if(usuario){
    const v = usuario.value.trim();
    const pat = usuario.getAttribute('pattern');
    if(usuario.hasAttribute('required') && v===''){
      e.preventDefault(); showInvalid(usuario, 'Usuario es requerido'); return;
    }
    if(v!=='' && pat){
      const re = new RegExp(pat);
      if(!re.test(v)){
        e.preventDefault(); showInvalid(usuario, 'Formato de usuario inválido. Usa: Apellido1, Apellido2, Nombre (sin . ; :)'); return;
      } else {
        removeFieldError(usuario);
      }
    }
  }

    if(telefono && telefono.value.trim()!==''){
    const v = telefono.value.trim();
    const pat = telefono.getAttribute('pattern');
    if(pat){ const re = new RegExp('^'+pat+'$'); if(!re.test(v)){ e.preventDefault(); showInvalid(telefono, 'Teléfono inválido — debe tener 9 dígitos'); return; } else { removeFieldError(telefono); } }
  }

  // remove inline errors when user starts typing
  [imei, usuario, telefono].forEach(function(inp){ if(!inp) return; inp.addEventListener('input', function(){
    if(!this.value) { removeFieldError(this); return; }
    // For imei, strip non-digits as the user types (but don't replace value automatically to avoid surprises)
    if(this.name === 'imei'){
      const digits = this.value.replace(/\D/g,'');
      // show tentative message if length not 15
      if(digits.length !== 15){
        // keep inline message but do not block typing
        removeFieldError(this);
        const msg = document.createElement('div'); msg.className = 'field-error-message'; msg.textContent = 'IMEI debe tener 15 dígitos'; this.insertAdjacentElement('afterend', msg);
        this.classList.add('input-error');
        return;
      } else {
        removeFieldError(this);
      }
    }
    const p = this.getAttribute('pattern');
    if(p){ try{ const re = new RegExp('^'+p+'$'); if(re.test(this.value.trim())) removeFieldError(this); }catch(e){} } else removeFieldError(this);
  }); });
});

// Agregar prefijo al salir del campo de teléfono
// No se añade prefijo automáticamente al perder el foco; la normalización la hace el servidor.

// Auto-limpiar IMEI en blur: dejar solo dígitos
document.querySelectorAll('[name=imei]').forEach(function(input){
  input.addEventListener('blur', function(){
    if(!this.value) return;
    const digits = this.value.replace(/\D/g,'');
    if(this.value !== digits) this.value = digits;
    // if not 15 digits, show inline message
    if(digits.length > 0 && digits.length !== 15){
      removeFieldError(this);
      this.classList.add('input-error');
      const msg = document.createElement('div'); msg.className = 'field-error-message'; msg.textContent = 'IMEI debe tener 15 dígitos'; this.insertAdjacentElement('afterend', msg);
    } else {
      removeFieldError(this);
    }
  });
});

// Tabla de histórico: seleccionar todo, exportar y botones
document.addEventListener('DOMContentLoaded', function(){
  // Ensure a global toast container attached to <body> so it isn't clipped by stacking contexts.
  // If a #toast-container exists in the DOM (rendered in templates), move it to document.body
  (function(){
    let toast = document.getElementById('toast-container');
    if(!toast){
      toast = document.createElement('div');
      toast.id = 'toast-container';
      toast.setAttribute('aria-live','polite');
      toast.setAttribute('aria-atomic','true');
      document.body.appendChild(toast);
    } else {
      // If it's not a direct child of body, move it to body to escape stacking contexts
      if(toast.parentNode !== document.body){
        document.body.appendChild(toast);
      }
    }
    // Force inline styles so they cannot be easily overridden by stacking contexts
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '99999';
    toast.style.display = 'flex';
    toast.style.flexDirection = 'column';
    toast.style.gap = '10px';
    toast.style.pointerEvents = 'none';
  })();
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
       // Detectar si estamos en /incidents, /history_entrega o /history_recepcion
       let exportUrl = '/history_entrega/export';
       if(window.location.pathname.includes('/incidents')){
         exportUrl = '/incidents/export';
       } else if(window.location.pathname.includes('/history_recepcion')){
         exportUrl = '/history_recepcion/export';
       }
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
      
      // Pedir confirmación (y contraseña si aplica)
      if(!confirm('¿Está seguro de que desea borrar los registros seleccionados? Esta acción no se puede deshacer.')){
        return;
      }
      
      // Crear y enviar formulario POST
      const form = document.createElement('form');
      form.method = 'POST';
      const currentPath = window.location.pathname;
      let deleteUrl = '/history_entrega/delete-selected';
      let requiresPassword = true;
      if(currentPath.includes('/incidents')){
        deleteUrl = '/incidents/delete-selected';
      } else if(currentPath.includes('/history_recepcion')){
        deleteUrl = '/history_recepcion/delete-selected';
      } else if(currentPath.includes('/inventario_telefonos')){
        deleteUrl = '/inventario_telefonos/delete-selected';
        requiresPassword = true;
      } else if(currentPath.includes('/history_computers')){
        deleteUrl = '/history_computers/delete-selected';
      }
      form.action = deleteUrl;
      
      const idsInput = document.createElement('input');
      idsInput.type = 'hidden';
      idsInput.name = 'ids';
      idsInput.value = ids.join(',');
      form.appendChild(idsInput);
      
      if(requiresPassword){
        const promptMsg = currentPath.includes('/inventario_telefonos') ? 'Introduce la contraseña de ADMIN para borrar:' : 'Introduce la contraseña para borrar:';
        const password = prompt(promptMsg);
        if(!password){
          return;
        }
        const passInput = document.createElement('input');
        passInput.type = 'hidden';
        passInput.name = currentPath.includes('/inventario_telefonos') ? 'admin_password' : 'password';
        passInput.value = password;
        form.appendChild(passInput);
      }
      
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

  // Mostrar / ocultar contraseña en login
  (function(){
    const toggle = document.getElementById('toggle-password');
    const pwd = document.getElementById('login-password');
    if(toggle && pwd){
      toggle.addEventListener('click', function(e){
        const isShown = pwd.type === 'text';
        if(isShown){
          pwd.type = 'password';
          toggle.setAttribute('aria-pressed','false');
          toggle.title = 'Mostrar contraseña';
          toggle.textContent = '👁️';
        } else {
          pwd.type = 'text';
          toggle.setAttribute('aria-pressed','true');
          toggle.title = 'Ocultar contraseña';
          toggle.textContent = '🙈';
        }
        pwd.focus();
      });
    }
  })();

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

  // --- Menús desplegables en el header ---
  document.addEventListener('click', function(e){
    const trigger = e.target.closest('.menu-trigger');
    if(trigger){
      e.stopPropagation();
      const dropdown = trigger.closest('.dropdown');
      const wasOpen = dropdown.classList.contains('open');
      
      // Cerrar todos los menús abiertos
      document.querySelectorAll('.dropdown.open').forEach(d => {
        d.classList.remove('open');
        const b = d.querySelector('.menu-trigger');
        if(b) b.setAttribute('aria-expanded', 'false');
      });

      if(!wasOpen){
        dropdown.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
      }
    } else {
      // Click fuera para cerrar todos
      if(!e.target.closest('.dropdown')){
        document.querySelectorAll('.dropdown.open').forEach(d => {
          d.classList.remove('open');
          const b = d.querySelector('.menu-trigger');
          if(b) b.setAttribute('aria-expanded', 'false');
        });
      }
    }
  });

  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape'){
      document.querySelectorAll('.dropdown.open').forEach(d => {
        d.classList.remove('open');
        const b = d.querySelector('.menu-trigger');
        if(b) b.setAttribute('aria-expanded', 'false');
      });
    }
  });

  // Cerrar al elegir una opción
  document.querySelectorAll('.dropdown-content').forEach(menuList => {
    menuList.addEventListener('click', function(e){
      const target = e.target.closest('a');
      if(target){
        const dropdown = this.closest('.dropdown');
        if(dropdown) dropdown.classList.remove('open');
      }
    });
  });

});

// Dropdown menu toggle function
function toggleDropdown(e){
  e.preventDefault();
  e.stopPropagation();
  const dropdownMenu = e.target.closest('.dropdown-menu');
  if(!dropdownMenu) return;
  
  // Cerrar todos los otros menús abiertos
  document.querySelectorAll('.dropdown-menu.open').forEach(menu => {
    if(menu !== dropdownMenu) menu.classList.remove('open');
  });
  
  // Toggle menú actual
  dropdownMenu.classList.toggle('open');
}

// Cerrar menús al hacer click fuera
document.addEventListener('click', function(e){
  if(!e.target.closest('.dropdown-menu')){
    document.querySelectorAll('.dropdown-menu.open').forEach(menu => {
      menu.classList.remove('open');
    });
  }
});

// Funcionalidad para la página Usuarios GTD SGPMR
document.addEventListener('DOMContentLoaded', function(){
  // Filtro por Usuario SGPMR
  const filterInput = document.getElementById('filter-usuario-sgpmr');
  if(filterInput){
    filterInput.addEventListener('input', function(){
      const filterValue = this.value.toLowerCase().trim();
      const tableRows = document.querySelectorAll('table tbody tr');
      
      tableRows.forEach(row => {
        // Skip the "no hay usuarios" row
        if(row.querySelector('td[colspan]')) return;
        
        const usuarioSGPMRCell = row.querySelector('td:nth-child(3)'); // Usuario SGPMR es la tercera columna
        if(usuarioSGPMRCell){
          const usuarioSGPMRValue = usuarioSGPMRCell.textContent.toLowerCase().trim();
          if(filterValue === '' || usuarioSGPMRValue.includes(filterValue)){
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        }
      });
    });
  }

  // Select all checkbox
  const selectAllUsuarios = document.getElementById('select-all-usuarios-checkbox');
  if(selectAllUsuarios){
    selectAllUsuarios.addEventListener('change', function(){
      const checked = this.checked;
      document.querySelectorAll('.row-select-usuarios').forEach(checkbox => {
        checkbox.checked = checked;
      });
    });
  }

  // Select all button
  const selectAllBtn = document.getElementById('select-all-usuarios');
  if(selectAllBtn){
    selectAllBtn.addEventListener('click', function(){
      document.querySelectorAll('.row-select-usuarios').forEach(checkbox => {
        checkbox.checked = true;
      });
      if(selectAllUsuarios) selectAllUsuarios.checked = true;
    });
  }

  // Deselect all button
  const deselectAllBtn = document.getElementById('deselect-all-usuarios');
  if(deselectAllBtn){
    deselectAllBtn.addEventListener('click', function(){
      document.querySelectorAll('.row-select-usuarios').forEach(checkbox => {
        checkbox.checked = false;
      });
      if(selectAllUsuarios) selectAllUsuarios.checked = false;
    });
  }

  // Delete selected usuarios
  const deleteBtn = document.getElementById('delete-selected-usuarios-btn');
  if(deleteBtn){
    deleteBtn.addEventListener('click', function(){
      const selected = document.querySelectorAll('.row-select-usuarios:checked');
      if(selected.length === 0){
        alert('Por favor selecciona al menos un usuario');
        return;
      }
      
      if(!confirm('¿Estás seguro de que quieres eliminar ' + selected.length + ' usuario(s)? Esta acción no se puede deshacer.')){
        return;
      }

      const password = prompt('Introduce la contraseña de ADMIN para confirmar:');
      if(!password) return;

      const ids = Array.from(selected).map(cb => cb.value);
      
      // Eliminar uno a uno
      let deleted = 0;
      let failed = false;
      ids.forEach(id => {
        const formData = new FormData();
        formData.append('admin_password', password);

        fetch(`/usuarios_gtd_sgpmr/${id}/eliminar`, {
          method: 'POST',
          body: formData
        }).then(res => {
          if(res.ok) {
            deleted++;
            // Eliminar la fila de la tabla
            const row = document.querySelector(`input[value="${id}"].row-select-usuarios`).closest('tr');
            if(row) row.remove();
          } else {
            failed = true;
          }
          
          if(deleted + (failed ? 1 : 0) === ids.length){
            if(failed && deleted === 0) {
              alert('Error: Contraseña de ADMIN incorrecta.');
            } else {
              alert('Proceso finalizado. Usuarios eliminados: ' + deleted);
            }
            location.reload();
          }
        });
      });
    });
  }

  // Exportar usuarios a CSV
  const exportBtn = document.getElementById('export-usuarios-btn');
  if(exportBtn){
    exportBtn.addEventListener('click', function(){
      const table = document.querySelector('table');
      if(!table) return;
      
      // Obtener encabezados (excluyendo checkbox y acciones)
      const headers = [];
      table.querySelectorAll('thead th').forEach((th, idx) => {
        if(idx === 0 || idx === table.querySelectorAll('thead th').length - 1) return; // Skip checkbox y acciones
        headers.push(th.textContent.trim());
      });
      
      // Obtener filas
      const rows = [];
      table.querySelectorAll('tbody tr').forEach(tr => {
        // Skip "no hay usuarios" row
        if(tr.querySelector('td[colspan]')) return;
        
        const rowData = [];
        tr.querySelectorAll('td').forEach((td, idx) => {
          // Skip checkbox (idx 0) y acciones (última columna)
          if(idx === 0 || idx === tr.querySelectorAll('td').length - 1) return;
          rowData.push(td.textContent.trim());
        });
        if(rowData.length > 0) rows.push(rowData);
      });
      
      // Crear CSV
      let csv = headers.join(',') + '\n';
      rows.forEach(row => {
        // Escapar comillas en los valores
        const escapedRow = row.map(cell => {
          if(cell.includes(',') || cell.includes('"') || cell.includes('\n')){
            return '"' + cell.replace(/"/g, '""') + '"';
          }
          return cell;
        }).join(',');
        csv += escapedRow + '\n';
      });
      
      // Descargar archivo
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'usuarios_gtd_sgpmr_' + new Date().toISOString().split('T')[0] + '.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});
// Filtro por IMEI en la página de Inventario de Teléfonos
document.addEventListener('DOMContentLoaded', function(){
  const filterInput = document.getElementById('filter-imei');
  if(filterInput){
    filterInput.addEventListener('input', function(){
      const filterValue = this.value.toLowerCase().trim();
      const tableRows = document.querySelectorAll('table tbody tr');
      
      tableRows.forEach(row => {
        // Skip the "no hay teléfonos" row
        if(row.querySelector('td[colspan]')) return;
        
        const imeiCell = row.querySelector('td:nth-child(2)'); // IMEI es la segunda columna
        if(imeiCell){
          const imeiValue = imeiCell.textContent.toLowerCase().trim();
          if(filterValue === '' || imeiValue.includes(filterValue)){
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        }
      });
    });
  }

  // Exportar tabla a CSV
  const exportBtn = document.getElementById('export-btn');
  if(exportBtn){
    exportBtn.addEventListener('click', function(){
      const table = document.querySelector('table');
      if(!table) return;
      
      // Obtener encabezados (excluyendo checkbox y acciones)
      const headers = [];
      table.querySelectorAll('thead th').forEach((th, idx) => {
        if(idx === 0 || idx === table.querySelectorAll('thead th').length - 1) return; // Skip checkbox y acciones
        headers.push(th.textContent.trim());
      });
      
      // Obtener filas visibles
      const rows = [];
      table.querySelectorAll('tbody tr').forEach(tr => {
        // Skip "no hay teléfonos" row y filas ocultas por filtro
        if(tr.querySelector('td[colspan]') || tr.style.display === 'none') return;
        
        const rowData = [];
        tr.querySelectorAll('td').forEach((td, idx) => {
          // Skip checkbox (idx 0) y acciones (última columna)
          if(idx === 0 || idx === tr.querySelectorAll('td').length - 1) return;
          rowData.push(td.textContent.trim());
        });
        if(rowData.length > 0) rows.push(rowData);
      });
      
      // Crear CSV
      let csv = headers.join(',') + '\n';
      rows.forEach(row => {
        // Escapar comillas en los valores
        const escapedRow = row.map(cell => {
          if(cell.includes(',') || cell.includes('"') || cell.includes('\n')){
            return '"' + cell.replace(/"/g, '""') + '"';
          }
          return cell;
        }).join(',');
        csv += escapedRow + '\n';
      });
      
      // Descargar archivo
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'inventario_telefonos_' + new Date().toISOString().split('T')[0] + '.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});

// Dropdown menu toggle function
function toggleDropdown(e){
  e.preventDefault();
  e.stopPropagation();
  const dropdownMenu = e.target.closest('.dropdown-menu');
  if(!dropdownMenu) return;
  
  // Cerrar todos los otros menús abiertos
  document.querySelectorAll('.dropdown-menu.open').forEach(menu => {
    if(menu !== dropdownMenu) menu.classList.remove('open');
  });
  
  // Toggle menú actual
  dropdownMenu.classList.toggle('open');
}

// Cerrar menús al hacer click fuera
document.addEventListener('click', function(e){
  if(!e.target.closest('.dropdown-menu')){
    document.querySelectorAll('.dropdown-menu.open').forEach(menu => {
      menu.classList.remove('open');
    });
  }
});
