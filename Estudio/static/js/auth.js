'use strict';

/**
 * Validación del formulario de login.
 */
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        const email = document.getElementById('id_email');
        const password = document.getElementById('id_password');
        let valid = true;

        if (!email || !email.value || !email.value.includes('@')) {
            if (email) email.classList.add('is-invalid');
            valid = false;
        } else {
            email.classList.remove('is-invalid');
        }

        if (!password || !password.value) {
            if (password) password.classList.add('is-invalid');
            valid = false;
        } else {
            password.classList.remove('is-invalid');
        }

        if (!valid) {
            e.preventDefault();
        }
    });
});
