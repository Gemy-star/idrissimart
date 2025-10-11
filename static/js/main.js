// ===========================
// Theme Toggle Functionality
// ===========================
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Check for saved theme preference or default to 'light'
const currentTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Add animation class
    themeToggle.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        themeToggle.style.transform = 'rotate(0deg)';
    }, 300);
});

// ===========================
// Language Switcher
// ===========================
document.querySelectorAll('.dropdown-item[data-lang]').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const lang = this.getAttribute('data-lang');

        // Store language preference
        localStorage.setItem('language', lang);

        // Update current language display
        document.querySelector('.current-lang').textContent = lang.toUpperCase();

        // Update check marks
        document.querySelectorAll('.lang-check').forEach(check => {
            check.style.visibility = 'hidden';
        });
        this.querySelector('.lang-check').style.visibility = 'visible';

        // Change page direction for RTL/LTR
        if (lang === 'ar') {
            document.documentElement.setAttribute('dir', 'rtl');
            document.documentElement.setAttribute('lang', 'ar');
            // Load Bootstrap RTL
            const bootstrapLink = document.querySelector('link[href*="bootstrap"]');
            if (bootstrapLink && !bootstrapLink.href.includes('rtl')) {
                bootstrapLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css';
            }
        } else {
            document.documentElement.setAttribute('dir', 'ltr');
            document.documentElement.setAttribute('lang', 'en');
            // Load Bootstrap LTR
            const bootstrapLink = document.querySelector('link[href*="bootstrap"]');
            if (bootstrapLink && bootstrapLink.href.includes('rtl')) {
                bootstrapLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css';
            }
        }

        // In production, you would redirect to the language-specific URL
        // window.location.href = `/${lang}${window.location.pathname}`;

        // Show notification
        showNotification(`Language changed to ${lang === 'ar' ? 'العربية' : 'English'}`);
    });
});

// ===========================
// Notification Function
// ===========================
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #4B315E 0%, #6B4C7A 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        font-weight: 600;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ===========================
// Initialize Swiper
// ===========================
const swiper = new Swiper('.mySwiper', {
    slidesPerView: 1,
    spaceBetween: 30,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false,
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    breakpoints: {
        640: {
            slidesPerView: 2,
            spaceBetween: 20,
        },
        1024: {
            slidesPerView: 3,
            spaceBetween: 30,
        },
    },
    effect: 'slide',
    speed: 600,
});

// ===========================
// GSAP Animations
// ===========================
gsap.registerPlugin(ScrollTrigger);

// Hero Animation
gsap.from('.hero-title', {
    opacity: 0,
    y: 50,
    duration: 1,
    ease: 'power3.out',
    delay: 0.2
});

gsap.from('.hero-subtitle', {
    opacity: 0,
    y: 30,
    duration: 1,
    delay: 0.5,
    ease: 'power3.out'
});

gsap.from('.btn-hero', {
    opacity: 0,
    y: 20,
    duration: 0.8,
    delay: 0.8,
    stagger: 0.2,
    ease: 'power3.out'
});

gsap.from('#heroImage', {
    opacity: 0,
    x: 100,
    duration: 1.2,
    delay: 0.6,
    ease: 'power3.out'
});

// Category Cards Animation
gsap.from('[data-category]', {
    scrollTrigger: {
        trigger: '.categories-section',
        start: 'top 80%',
    },
    opacity: 0,
    y: 50,
    duration: 0.8,
    stagger: 0.15,
    ease: 'power3.out'
});

// Section Titles Animation
gsap.utils.toArray('.section-title').forEach(title => {
    gsap.from(title, {
        scrollTrigger: {
            trigger: title,
            start: 'top 85%',
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    });
});

// Features Animation
gsap.from('.feature-box', {
    scrollTrigger: {
        trigger: '.features-section',
        start: 'top 80%',
    },
    opacity: 0,
    y: 40,
    duration: 0.8,
    stagger: 0.2,
    ease: 'power3.out'
});

// Footer Animation
gsap.from('.footer .col-lg-4, .footer .col-lg-2, .footer .col-lg-3', {
    scrollTrigger: {
        trigger: '.footer',
        start: 'top 90%',
    },
    opacity: 0,
    y: 30,
    duration: 0.6,
    stagger: 0.1,
    ease: 'power3.out'
});

// ===========================
// Navbar Scroll Effect
// ===========================
let lastScroll = 0;
const navbar = document.getElementById('mainNav');

window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
        navbar.style.padding = '0.5rem 0';
        navbar.style.boxShadow = '0 6px 30px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.padding = '1rem 0';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
    }

    // Hide/Show navbar on scroll
    if (currentScroll > lastScroll && currentScroll > 500) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }

    lastScroll = currentScroll;
});

// ===========================
// Smooth Scrolling
// ===========================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 80; // Account for fixed navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// ===========================
// Loading Animation
// ===========================
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// ===========================
// Category Card Click Animation
// ===========================
document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('click', function() {
        // Add click animation
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = '';
        }, 200);
    });
});

// ===========================
// Parallax Effect on Hero
// ===========================
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroContent = document.querySelector('.hero-content');
    const heroImage = document.getElementById('heroImage');

    if (heroContent && scrolled < 800) {
        heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
        if (heroImage) {
            heroImage.style.transform = `translateY(${scrolled * 0.2}px)`;
        }
    }
});

// ===========================
// Button Ripple Effect
// ===========================
document.querySelectorAll('.btn-custom, .btn-hero').forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple animation
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// ===========================
// Counter Animation for Stats
// ===========================
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// ===========================
// Intersection Observer for Lazy Loading
// ===========================
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.add('loaded');
            observer.unobserve(img);
        }
    });
});

document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});

// ===========================
// Console Welcome Message
// ===========================
console.log('%c🚀 إدريسي مارت', 'color: #4B315E; font-size: 24px; font-weight: bold;');
console.log('%cWelcome to Idrisi Mart! 🎉', 'color: #FF6001; font-size: 16px;');
console.log('%cBuilt with ❤️ using Django + Bootstrap 5 + GSAP + Swiper', 'color: #666; font-size: 12px;');

// ===========================
// Performance Optimization
// ===========================
// Debounce function for scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll handlers
const debouncedScroll = debounce(() => {
    // Additional scroll handlers can go here
}, 100);

window.addEventListener('scroll', debouncedScroll);

// ===========================
// Accessibility Improvements
// ===========================
// Add keyboard navigation support
document.querySelectorAll('.category-card').forEach(card => {
    card.setAttribute('tabindex', '0');
    card.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            this.click();
        }
    });
});

// ===========================
// Print current theme on load
// ===========================
console.log(`Current theme: ${html.getAttribute('data-theme')}`);
console.log(`Current language: ${document.documentElement.getAttribute('lang')}`);
