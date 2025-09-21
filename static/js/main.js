// Funcionalidades JavaScript para el Sistema de Notas
// Evitar conflictos con otros scripts
// Última actualización: 1758469500

(function() {
    'use strict';
    
    // Verificar que no hay conflictos
    if (window.SistemaNotasLoaded) {
        return;
    }
    window.SistemaNotasLoaded = true;

document.addEventListener('DOMContentLoaded', function() {
    // Animaciones suaves para los botones
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Validación de formularios (excluyendo el formulario de login, registro de alumnos, crear usuario, crear materia, agregar nota, editar nota y editar alumno)
    const forms = document.querySelectorAll('form:not(#loginForm):not([action*="registrar_alumno"]):not([action*="crear_usuario"]):not([action*="crear_materia"]):not([action*="agregar_nota"]):not([action*="editar_nota"]):not([action*="editar_alumno"])');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#f56565';
                    isValid = false;
                } else {
                    field.style.borderColor = '#e2e8f0';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Por favor, completa todos los campos requeridos', 'error');
            }
        });
    });

    // Validación específica para DNI
    const dniInput = document.getElementById('dni');
    if (dniInput) {
        dniInput.addEventListener('input', function() {
            const value = this.value.replace(/\D/g, ''); // Solo números
            this.value = value;
            
            if (value.length > 8) {
                this.value = value.substring(0, 8);
            }
        });
    }

    // Validación para notas
    const notaInput = document.getElementById('nota');
    if (notaInput) {
        notaInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.value = 0;
            } else if (value > 20) {
                this.value = 20;
            }
        });
    }

    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Búsqueda en tiempo real para tablas (si es necesario)
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('.table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Confirmación para acciones importantes
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        if (button.textContent.includes('Eliminar') || button.textContent.includes('Delete')) {
            button.addEventListener('click', function(e) {
                if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Mejorar la experiencia en móviles
    if (window.innerWidth <= 768) {
        // Ajustar el viewport para evitar zoom en inputs
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
        }
    }

    // TODOS LOS BOTONES DE SUBMIT FUNCIONAN DE MANERA COMPLETAMENTE NATIVA
    // Sin JavaScript que interfiera con el envío de formularios
});

// Función para mostrar alertas personalizadas
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide después de 5 segundos
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => {
                alertDiv.remove();
            }, 300);
        }, 5000);
    }
}

// Función para formatear números
function formatNumber(num) {
    return num.toFixed(1);
}

// Función para validar email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Función para validar DNI
function validateDNI(dni) {
    const re = /^\d{7,8}$/;
    return re.test(dni);
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copiado al portapapeles', 'success');
    }).catch(() => {
        showAlert('Error al copiar', 'error');
    });
}

// Función para exportar datos (futura implementación)
function exportData(format = 'csv') {
    showAlert('Función de exportación en desarrollo', 'info');
}

// Función para imprimir
function printPage() {
    window.print();
}

// Función para modo oscuro (futura implementación)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Cargar preferencias guardadas
function loadPreferences() {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Inicializar preferencias al cargar la página
loadPreferences();

})(); // Cerrar la función auto-ejecutable
