// Sistema de Alertas Moderno (Toast) - Global
document.addEventListener('DOMContentLoaded', function() {
    const toasts = document.querySelectorAll('.toast[data-autohide="true"]');
    
    toasts.forEach(function(toast) {
        const delay = parseInt(toast.getAttribute('data-delay')) || 5000;
        
        // Mostrar toast con animación
        setTimeout(function() {
            toast.classList.add('show');
        }, 100);
        
        // Auto-ocultar
        setTimeout(function() {
            hideToast(toast);
        }, delay);
        
        // Iniciar barra de progreso
        const progressBar = toast.querySelector('.toast-progress-bar');
        if (progressBar) {
            progressBar.style.animation = `progress ${delay}ms linear forwards`;
        }
    });
});

function hideToast(toast) {
    toast.classList.remove('show');
    toast.classList.add('hide');
    setTimeout(function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function closeToast(button) {
    const toast = button.closest('.toast');
    hideToast(toast);
}

// Función para mostrar toast programáticamente
function showToast(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('data-autohide', 'true');
    toast.setAttribute('data-delay', duration);
    
    const iconMap = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    const titleMap = {
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'info': 'Información'
    };
    
    toast.innerHTML = `
        <div class="toast-header">
            <div class="toast-icon">
                <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${titleMap[type] || 'Información'}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="closeToast(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="toast-progress">
            <div class="toast-progress-bar"></div>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Inicializar el toast
    setTimeout(function() {
        toast.classList.add('show');
    }, 100);
    
    // Auto-ocultar
    setTimeout(function() {
        hideToast(toast);
    }, duration);
    
    // Iniciar barra de progreso
    const progressBar = toast.querySelector('.toast-progress-bar');
    if (progressBar) {
        progressBar.style.animation = `progress ${duration}ms linear forwards`;
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}
