/**
 * =============================================================================
 * ESTUDIO RIVAROSSA Y ASOCIADOS
 * JavaScript Principal - ES6+
 * 
 * Funcionalidades:
 * - Dark Mode Toggle
 * - Micro-interacciones
 * - Animaciones suaves
 * - Validaciones de formularios
 * - Mejoras de UX/UI
 * =============================================================================
 */

'use strict';

// =============================================================================
// DARK MODE - Sistema de temas
// =============================================================================

const ThemeManager = (() => {
    const THEME_KEY = 'estudio-theme';
    const THEME_ATTRIBUTE = 'data-theme';
    
    /**
     * Obtiene el tema actual (de localStorage o del sistema)
     */
    const getCurrentTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme) {
            return savedTheme;
        }
        
        // Si no hay tema guardado, usar preferencia del sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    };
    
    /**
     * Aplica el tema al documento
     */
    const applyTheme = (theme) => {
        document.documentElement.setAttribute(THEME_ATTRIBUTE, theme);
        localStorage.setItem(THEME_KEY, theme);
        
        // Actualizar meta theme-color para la barra del navegador móvil
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1d24' : '#8C4F9F');
        }
        
        // Actualizar ícono del toggle
        updateThemeIcon(theme);
    };
    
    /**
     * Actualiza el ícono del botón de tema
     */
    const updateThemeIcon = (theme) => {
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(button => {
            const icon = button.querySelector('i');
            if (icon) {
                if (theme === 'dark') {
                    icon.className = 'bi bi-sun-fill';
                } else {
                    icon.className = 'bi bi-moon-stars-fill';
                }
            }
        });
    };
    
    /**
     * Alterna entre tema claro y oscuro
     */
    const toggleTheme = () => {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    };
    
    /**
     * Inicializa el sistema de temas
     */
    const init = () => {
        // Aplicar tema inicial
        const initialTheme = getCurrentTheme();
        applyTheme(initialTheme);
        
        // Configurar toggles
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', toggleTheme);
        });
        
        // Escuchar cambios en preferencia del sistema
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem(THEME_KEY)) {
                    applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    };
    
    return {
        init,
        toggleTheme,
        getCurrentTheme,
        applyTheme
    };
})();

// =============================================================================
// ANIMACIONES Y MICRO-INTERACCIONES
// =============================================================================

const AnimationManager = (() => {
    /**
     * Animación de entrada para elementos
     */
    const fadeInElements = () => {
        const elements = document.querySelectorAll('[data-animate="fade-in"]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '0';
                        entry.target.style.transform = 'translateY(20px)';
                        entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                        
                        requestAnimationFrame(() => {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        });
                    }, index * 100);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        elements.forEach(element => observer.observe(element));
    };
    
    /**
     * Animación de cards con delay progresivo
     */
    const animateCards = () => {
        const cards = document.querySelectorAll('.card, .card-studio');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 80);
        });
    };
    
    /**
     * Smooth scroll para enlaces internos
     */
    const initSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    };
    
    /**
     * Efecto de paralaje sutil en el hero
     */
    const initParallax = () => {
        const hero = document.querySelector('.hero-studio');
        if (!hero) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        });
    };
    
    /**
     * Contador animado para estadísticas
     */
    const animateCounters = () => {
        const counters = document.querySelectorAll('[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const updateCounter = () => {
                            current += step;
                            if (current < target) {
                                counter.textContent = Math.floor(current);
                                requestAnimationFrame(updateCounter);
                            } else {
                                counter.textContent = target;
                            }
                        };
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(counter);
        });
    };
    
    const init = () => {
        fadeInElements();
        animateCards();
        initSmoothScroll();
        initParallax();
        animateCounters();
    };
    
    return { init };
})();

// =============================================================================
// ALERTAS Y NOTIFICACIONES
// =============================================================================

const AlertManager = (() => {
    /**
     * Auto-cierre de alertas después de un tiempo
     */
    const initAutoClose = () => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000);
        });
    };
    
    /**
     * Crea una alerta dinámica
     */
    const createAlert = (message, type = 'info', dismissible = true) => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} ${dismissible ? 'alert-dismissible fade show' : ''} alert-studio-${type}`;
        alertDiv.role = 'alert';
        
        alertDiv.innerHTML = `
            <i class="bi ${getIconForType(type)} me-2"></i>
            ${message}
            ${dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' : ''}
        `;
        
        return alertDiv;
    };
    
    /**
     * Obtiene el ícono según el tipo de alerta
     */
    const getIconForType = (type) => {
        const icons = {
            'success': 'bi-check-circle-fill',
            'danger': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'info': 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    };
    
    const init = () => {
        initAutoClose();
    };
    
    return {
        init,
        createAlert
    };
})();

// =============================================================================
// FORMULARIOS
// =============================================================================

const FormManager = (() => {
    /**
     * Alterna la visibilidad de un campo de contraseña
     */
    const togglePassword = (inputId, button) => {
        const input = document.getElementById(inputId);
        if (!input) return;
        
        const icon = button.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            if (icon) icon.className = 'bi bi-eye-slash';
        } else {
            input.type = 'password';
            if (icon) icon.className = 'bi bi-eye';
        }
    };
    
    /**
     * Validación de email
     */
    const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };
    
    /**
     * Validación de contraseña
     */
    const validatePassword = (password) => {
        return {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
    };
    
    /**
     * Validación de formularios en tiempo real
     */
    const initFormValidation = () => {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    };
    
    /**
     * Feedback visual mejorado para inputs
     */
    const initInputFeedback = () => {
        const inputs = document.querySelectorAll('.input-studio, .form-control');
        
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement?.classList.add('input-focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement?.classList.remove('input-focused');
            });
        });
    };
    
    const init = () => {
        initFormValidation();
        initInputFeedback();
        
        // Exponer togglePassword como global para uso en templates
        window.togglePassword = togglePassword;
    };
    
    return {
        init,
        togglePassword,
        isValidEmail,
        validatePassword
    };
})();

// =============================================================================
// NAVBAR - Scroll behavior
// =============================================================================

const NavbarManager = (() => {
    /**
     * Navbar con sombra al hacer scroll
     */
    const initScrollBehavior = () => {
        const navbar = document.querySelector('.navbar, .navbar-studio');
        if (!navbar) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
                navbar.style.boxShadow = 'var(--shadow-md)';
            } else {
                navbar.classList.remove('navbar-scrolled');
                navbar.style.boxShadow = 'var(--shadow-sm)';
            }
        });
    };
    
    const init = () => {
        initScrollBehavior();
    };
    
    return { init };
})();

// =============================================================================
// UTILIDADES GENERALES
// =============================================================================

const Utils = (() => {
    /**
     * Confirmación de acciones
     */
    const confirmAction = (message) => {
        return confirm(message || '¿Estás seguro de realizar esta acción?');
    };
    
    /**
     * Copiar texto al portapapeles
     */
    const copyToClipboard = async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Error al copiar:', err);
            return false;
        }
    };
    
    /**
     * Detectar dispositivo móvil
     */
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };
    
    /**
     * Debounce para optimizar eventos
     */
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    return {
        confirmAction,
        copyToClipboard,
        isMobile,
        debounce
    };
})();

// =============================================================================
// INICIALIZACIÓN
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar todos los módulos
    ThemeManager.init();
    AnimationManager.init();
    AlertManager.init();
    FormManager.init();
    NavbarManager.init();
    
    // Prevención de envío múltiple de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.setAttribute('data-original-text', submitBtn.innerHTML);
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Procesando...';

                // Re-habilitar después de 10 segundos (por si hay un error)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Enviar';
                }, 10000);
            }
        });
    });
    
    console.log('%c🏢 Estudio Rivarossa y Asociados', 'color: #8C4F9F; font-size: 16px; font-weight: bold;');
    console.log('%cSistema inicializado correctamente', 'color: #233142; font-size: 12px;');
});

// Exponer utilidades globales
window.EstudioUtils = Utils;
window.EstudioTheme = ThemeManager;
window.EstudioAlerts = AlertManager;
