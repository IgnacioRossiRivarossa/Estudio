'use strict';

const ThemeManager = (() => {
    const THEME_KEY = 'estudio-theme';
    const THEME_ATTRIBUTE = 'data-theme';
    const getCurrentTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme) {
            return savedTheme;
        }
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    };
    const applyTheme = (theme) => {
        document.documentElement.setAttribute(THEME_ATTRIBUTE, theme);
        localStorage.setItem(THEME_KEY, theme);
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1d24' : '#8C4F9F');
        }
        updateThemeIcon(theme);
    };
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
    const toggleTheme = () => {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    };
    const init = () => {
        const initialTheme = getCurrentTheme();
        applyTheme(initialTheme);
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', toggleTheme);
        });
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

const AnimationManager = (() => {
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

    const initParallax = () => {
        const hero = document.querySelector('.hero-studio');
        if (!hero) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        });
    };

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

const AlertManager = (() => {
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

const FormManager = (() => {
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

    const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password) => {
        return {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
    };

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
        window.togglePassword = togglePassword;
    };
    
    return {
        init,
        togglePassword,
        isValidEmail,
        validatePassword
    };
})();

const NavbarManager = (() => {
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

const Utils = (() => {
    const confirmAction = (message) => {
        return confirm(message || '¿Estás seguro de realizar esta acción?');
    };
    const copyToClipboard = async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Error al copiar:', err);
            return false;
        }
    };
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };
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

document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    AnimationManager.init();
    AlertManager.init();
    FormManager.init();
    NavbarManager.init();
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.setAttribute('data-original-text', submitBtn.innerHTML);
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Procesando...';

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

window.EstudioUtils = Utils;
window.EstudioTheme = ThemeManager;
window.EstudioAlerts = AlertManager;
