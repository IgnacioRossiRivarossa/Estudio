'use strict';

/**
 * Módulo reutilizable para validación de contraseñas en tiempo real.
 * Se usa en activate.html y password_reset_confirm.html.
 */
const PasswordValidation = (() => {
    let field1 = null;
    let field2 = null;

    const updateReq = (id, valid) => {
        const el = document.getElementById(id);
        if (!el) return;
        const icon = el.querySelector('i');
        if (icon) {
            icon.className = valid
                ? 'bi bi-check-circle text-success'
                : 'bi bi-x-circle text-danger';
        }
    };

    const checkMatch = () => {
        const feedback = document.getElementById('matchFeedback');
        if (!feedback || !field2) return;

        if (field2.value) {
            feedback.style.display = 'block';
            if (field1.value === field2.value) {
                feedback.innerHTML =
                    '<i class="bi bi-check-circle text-success"></i> Las contraseñas coinciden';
            } else {
                feedback.innerHTML =
                    '<i class="bi bi-x-circle text-danger"></i> Las contraseñas no coinciden';
            }
        } else {
            feedback.style.display = 'none';
        }
    };

    const init = (password1Id, password2Id) => {
        field1 = document.getElementById(password1Id || 'id_password1');
        field2 = document.getElementById(password2Id || 'id_password2');

        if (field1) {
            field1.addEventListener('input', () => {
                const val = field1.value;
                updateReq('req-length', val.length >= 8);
                updateReq('req-upper', /[A-Z]/.test(val));
                updateReq('req-number', /[0-9]/.test(val));
                checkMatch();
            });
        }

        if (field2) {
            field2.addEventListener('input', checkMatch);
        }
    };

    return { init };
})();

document.addEventListener('DOMContentLoaded', () => {
    PasswordValidation.init();
});
