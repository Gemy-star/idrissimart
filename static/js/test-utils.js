// ===========================
// Testing & Debugging Utilities
// FILE: static/js/test-utils.js
// ===========================

/**
 * Idrisi Mart Testing Console
 * Open browser console and type: IdrissiTest.runAll()
 */
window.IdrissiTest = {

    /**
     * Test cart functionality
     */
    testCart: function() {
        console.log('%c🛒 Testing Cart...', 'color: #4B315E; font-size: 16px; font-weight: bold;');

        // Test add to cart
        console.log('Adding test item to cart...');
        CartWishlist.addToCart('test-123', 'Test Product').then(result => {
            console.log('✅ Add to cart:', result);
        });

        // Test badge update
        setTimeout(() => {
            console.log('Updating cart badge...');
            CartWishlist.updateBadgeCount('cart', 10);
            console.log('✅ Badge updated to 10');
        }, 1000);

        // Test remove from cart
        setTimeout(() => {
            console.log('Removing test item...');
            CartWishlist.removeFromCart('test-123', 'Test Product').then(result => {
                console.log('✅ Remove from cart:', result);
            });
        }, 2000);
    },

    /**
     * Test wishlist functionality
     */
    testWishlist: function() {
        console.log('%c❤️ Testing Wishlist...', 'color: #FF6001; font-size: 16px; font-weight: bold;');

        console.log('Adding test item to wishlist...');
        CartWishlist.addToWishlist('test-456', 'Test Product').then(result => {
            console.log('✅ Add to wishlist:', result);
        });

        setTimeout(() => {
            console.log('Updating wishlist badge...');
            CartWishlist.updateBadgeCount('wishlist', 5);
            console.log('✅ Badge updated to 5');
        }, 1000);

        setTimeout(() => {
            console.log('Removing test item...');
            CartWishlist.removeFromWishlist('test-456', 'Test Product').then(result => {
                console.log('✅ Remove from wishlist:', result);
            });
        }, 2000);
    },

    /**
     * Test notifications
     */
    testNotifications: function() {
        console.log('%c🔔 Testing Notifications...', 'color: #27ae60; font-size: 16px; font-weight: bold;');

        setTimeout(() => {
            CartWishlist.showNotification('This is a success message', 'success');
        }, 500);

        setTimeout(() => {
            CartWishlist.showNotification('This is an error message', 'error');
        }, 1500);

        setTimeout(() => {
            CartWishlist.showNotification('This is an info message', 'info');
        }, 2500);

        console.log('✅ Notifications triggered');
    },

    /**
     * Test animations
     */
    testAnimations: function() {
        console.log('%c✨ Testing Animations...', 'color: #9b59b6; font-size: 16px; font-weight: bold;');

        // Test card animation
        const cards = document.querySelectorAll('.category-card, .product-card');
        if (cards.length > 0) {
            gsap.from(cards, {
                opacity: 0,
                y: 50,
                duration: 0.8,
                stagger: 0.1,
                ease: 'power3.out'
            });
            console.log(`✅ Animated ${cards.length} cards`);
        } else {
            console.log('⚠️ No cards found');
        }

        // Test button ripple
        const buttons = document.querySelectorAll('.btn-custom');
        if (buttons.length > 0) {
            console.log(`✅ Found ${buttons.length} buttons with ripple effect`);
        }
    },

    /**
     * Test country selector
     */
    testCountrySelector: function() {
        console.log('%c🌍 Testing Country Selector...', 'color: #3498db; font-size: 16px; font-weight: bold;');

        const savedCountry = localStorage.getItem('selectedCountry');
        console.log('Current country:', savedCountry || 'None');

        // Test switching countries
        const testCountries = ['SA', 'AE', 'EG'];
        testCountries.forEach((code, index) => {
            setTimeout(() => {
                localStorage.setItem('selectedCountry', code);
                console.log(`✅ Switched to country: ${code}`);

                if (index === testCountries.length - 1) {
                    // Restore original
                    setTimeout(() => {
                        if (savedCountry) {
                            localStorage.setItem('selectedCountry', savedCountry);
                        }
                        console.log('✅ Restored original country');
                    }, 1000);
                }
            }, (index + 1) * 1000);
        });
    },

    /**
     * Test theme toggle
     */
    testTheme: function() {
        console.log('%c🌓 Testing Theme Toggle...', 'color: #f39c12; font-size: 16px; font-weight: bold;');

        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        console.log('Current theme:', currentTheme);

        // Toggle theme
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', newTheme);
        console.log('✅ Switched to:', newTheme);

        // Restore after 2 seconds
        setTimeout(() => {
            html.setAttribute('data-theme', currentTheme);
            console.log('✅ Restored to:', currentTheme);
        }, 2000);
    },

    /**
     * Check session data
     */
    checkSession: function() {
        console.log('%c💾 Session Data...', 'color: #e67e22; font-size: 16px; font-weight: bold;');

        console.log('LocalStorage:');
        console.log('  - Theme:', localStorage.getItem('theme'));
        console.log('  - Language:', localStorage.getItem('language'));
        console.log('  - Country:', localStorage.getItem('selectedCountry'));

        console.log('\nCookies:');
        const cookies = document.cookie.split(';').map(c => c.trim());
        cookies.forEach(cookie => {
            console.log('  -', cookie);
        });
    },

    /**
     * Performance check
     */
    checkPerformance: function() {
        console.log('%c⚡ Performance Check...', 'color: #1abc9c; font-size: 16px; font-weight: bold;');

        if (window.performance) {
            const perf = window.performance.timing;
            const loadTime = perf.loadEventEnd - perf.navigationStart;
            const domReadyTime = perf.domContentLoadedEventEnd - perf.navigationStart;

            console.log(`Page Load Time: ${loadTime}ms`);
            console.log(`DOM Ready Time: ${domReadyTime}ms`);

            if (loadTime < 2000) {
                console.log('✅ Great performance!');
            } else if (loadTime < 4000) {
                console.log('⚠️ Good, but can be improved');
            } else {
                console.log('❌ Needs optimization');
            }
        } else {
            console.log('⚠️ Performance API not available');
        }
    },

    /**
     * Check responsive design
     */
    checkResponsive: function() {
        console.log('%c📱 Responsive Check...', 'color: #e74c3c; font-size: 16px; font-weight: bold;');

        const width = window.innerWidth;
        console.log(`Screen width: ${width}px`);

        if (width < 576) {
            console.log('📱 Extra small device (mobile)');
        } else if (width < 768) {
            console.log('📱 Small device (large mobile)');
        } else if (width < 992) {
            console.log('💻 Medium device (tablet)');
        } else if (width < 1200) {
            console.log('💻 Large device (desktop)');
        } else {
            console.log('🖥️ Extra large device (large desktop)');
        }

        // Check critical elements
        const navbar = document.querySelector('.navbar');
        const footer = document.querySelector('.footer');

        if (navbar) {
            const navHeight = navbar.offsetHeight;
            console.log(`✅ Navbar height: ${navHeight}px`);
        }

        if (footer) {
            console.log('✅ Footer exists');
        }
    },

    /**
     * Accessibility check
     */
    checkAccessibility: function() {
        console.log('%c♿ Accessibility Check...', 'color: #34495e; font-size: 16px; font-weight: bold;');

        // Check for alt attributes on images
        const images = document.querySelectorAll('img');
        const imagesWithoutAlt = Array.from(images).filter(img => !img.alt);

        if (imagesWithoutAlt.length > 0) {
            console.warn(`⚠️ ${imagesWithoutAlt.length} images without alt text`);
        } else {
            console.log('✅ All images have alt text');
        }

        // Check for aria-labels on buttons
        const buttons = document.querySelectorAll('button');
        const buttonsWithoutLabel = Array.from(buttons).filter(btn =>
            !btn.getAttribute('aria-label') && !btn.textContent.trim()
        );

        if (buttonsWithoutLabel.length > 0) {
            console.warn(`⚠️ ${buttonsWithoutLabel.length} buttons without labels`);
        } else {
            console.log('✅ All buttons have labels');
        }

        // Check color contrast
        console.log('💡 Tip: Use browser DevTools to check color contrast ratios');
    },

    /**
     * Generate dummy data
     */
    generateDummyData: function() {
        console.log('%c📦 Generating Dummy Data...', 'color: #8e44ad; font-size: 16px; font-weight: bold;');

        // Add dummy items to cart
        for (let i = 1; i <= 5; i++) {
            CartWishlist.addToCart(`dummy-${i}`, `Dummy Product ${i}`);
        }

        // Add dummy items to wishlist
        for (let i = 1; i <= 3; i++) {
            CartWishlist.addToWishlist(`dummy-wish-${i}`, `Wishlist Item ${i}`);
        }

        console.log('✅ Added 5 items to cart and 3 items to wishlist');
    },

    /**
     * Clear all data
     */
    clearAllData: function() {
        console.log('%c🗑️ Clearing All Data...', 'color: #c0392b; font-size: 16px; font-weight: bold;');

        // Clear localStorage
        localStorage.clear();
        console.log('✅ LocalStorage cleared');

        // Clear sessionStorage
        sessionStorage.clear();
        console.log('✅ SessionStorage cleared');

        console.log('⚠️ You may need to refresh the page');
    },

    /**
     * Run all tests
     */
    runAll: function() {
        console.log('%c🚀 Running All Tests...', 'color: #2c3e50; font-size: 20px; font-weight: bold;');
        console.log('='.repeat(50));

        this.checkSession();
        console.log('\n');

        this.checkPerformance();
        console.log('\n');

        this.checkResponsive();
        console.log('\n');

        this.checkAccessibility();
        console.log('\n');

        setTimeout(() => {
            this.testNotifications();
        }, 1000);

        setTimeout(() => {
            this.testCart();
        }, 5000);

        setTimeout(() => {
            this.testWishlist();
        }, 9000);

        console.log('\n');
        console.log('%c✅ All tests scheduled! Check console for results.', 'color: #27ae60; font-size: 16px; font-weight: bold;');
        console.log('='.repeat(50));
    },

    /**
     * Show help
     */
    help: function() {
        console.log('%c📖 Idrisi Mart Testing Utilities', 'color: #2c3e50; font-size: 20px; font-weight: bold;');
        console.log('\nAvailable commands:');
        console.log('  IdrissiTest.runAll()              - Run all tests');
        console.log('  IdrissiTest.testCart()            - Test cart functionality');
        console.log('  IdrissiTest.testWishlist()        - Test wishlist functionality');
        console.log('  IdrissiTest.testNotifications()   - Test notifications');
        console.log('  IdrissiTest.testAnimations()      - Test animations');
        console.log('  IdrissiTest.testCountrySelector() - Test country selector');
        console.log('  IdrissiTest.testTheme()           - Test theme toggle');
        console.log('  IdrissiTest.checkSession()        - Check session data');
        console.log('  IdrissiTest.checkPerformance()    - Check performance');
        console.log('  IdrissiTest.checkResponsive()     - Check responsive design');
        console.log('  IdrissiTest.checkAccessibility()  - Check accessibility');
        console.log('  IdrissiTest.generateDummyData()   - Generate dummy data');
        console.log('  IdrissiTest.clearAllData()        - Clear all data');
        console.log('  IdrissiTest.help()                - Show this help');
    }
};

// Auto-show help on load
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('%c🎉 Idrisi Mart Development Mode', 'color: #4B315E; font-size: 18px; font-weight: bold;');
    console.log('%cType IdrissiTest.help() for testing utilities', 'color: #666; font-size: 14px;');
}
