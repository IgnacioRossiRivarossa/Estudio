/**
 * Estudio - JavaScript Principal
 * 
 * Funcionalidades:
 * - Mostrar/ocultar contraseñas
 * - Auto-cierre de alertas
 * - Confirmaciones de acciones
 * - Mejoras de UX
 */

'use strict';

// =============================================================================
// MOSTRAR/OCULTAR CONTRASEÑA
// =============================================================================

/**
 * Alterna la visibilidad de un campo de contraseña.
 * @param {string} inputId - ID del campo de contraseña.
 * @param {HTMLElement} button - Botón que disparó la acción.
 */
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const icon = button.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

// =============================================================================
// AUTO-CIERRE DE ALERTAS
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    // Cerrar alertas automáticamente después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Animación de entrada para cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function (card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        setTimeout(function () {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// =============================================================================
// CONFIRMACIONES DE ACCIONES
// =============================================================================

/**
 * Muestra un diálogo de confirmación antes de ejecutar una acción.
 * @param {string} message - Mensaje de confirmación.
 * @returns {boolean} - true si el usuario confirma.
 */
function confirmAction(message) {
    return confirm(message || '¿Estás seguro de realizar esta acción?');
}

// =============================================================================
// VALIDACIONES DE FORMULARIOS
// =============================================================================

/**
 * Valida un campo de email.
 * @param {string} email - Dirección de email a validar.
 * @returns {boolean} - true si es un email válido.
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Valida requisitos de contraseña.
 * @param {string} password - Contraseña a validar.
 * @returns {object} - Objeto con el resultado de cada validación.
 */
function validatePassword(password) {
    return {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
    };
}

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Previene envío múltiple de formularios.
 * Deshabilita el botón de submit después del primer clic.
 */
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Procesando...';

                // Re-habilitar después de 10 segundos (por si hay un error)
                setTimeout(function () {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Enviar';
                }, 10000);
            }
        });
    });

    // Guardar texto original de botones
    const submitButtons = document.querySelectorAll('[type="submit"]');
    submitButtons.forEach(function (btn) {
        btn.setAttribute('data-original-text', btn.innerHTML);
    });
});
