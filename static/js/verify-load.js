// ===========================
// GSAP & Dependencies Verification
// Place this AFTER all scripts load
// ===========================

(function() {
    'use strict';

    console.log('%c🔍 Verifying Dependencies...', 'color:#3498db;font-size:14px;font-weight:bold;');

    const checks = {
        'GSAP Core': typeof window.gsap !== 'undefined',
        'GSAP ScrollTrigger': typeof window.ScrollTrigger !== 'undefined',
        'Bootstrap': typeof window.bootstrap !== 'undefined',
        'Swiper': typeof window.Swiper !== 'undefined',
        'jQuery (optional)': typeof window.$ !== 'undefined'
    };

    let allPassed = true;

    Object.entries(checks).forEach(([name, passed]) => {
        if (passed) {
            console.log(`%c✓ ${name}`, 'color:#27ae60;font-weight:bold;');
        } else {
            console.log(`%c✗ ${name}`, 'color:#e74c3c;font-weight:bold;');
            if (name.includes('GSAP') || name.includes('Bootstrap') || name.includes('Swiper')) {
                allPassed = false;
            }
        }
    });

    if (allPassed) {
        console.log('%c✅ All critical dependencies loaded!', 'color:#27ae60;font-size:14px;font-weight:bold;');
    } else {
        console.error('%c❌ Some critical dependencies failed to load!', 'color:#e74c3c;font-size:14px;font-weight:bold;');
    }

    // Test GSAP functionality
    if (window.gsap) {
        try {
            // Simple test animation
            const testDiv = document.createElement('div');
            testDiv.style.opacity = '0';
            document.body.appendChild(testDiv);

            gsap.to(testDiv, {
                opacity: 1,
                duration: 0.1,
                onComplete: () => {
                    console.log('%c✓ GSAP animations working', 'color:#27ae60;font-weight:bold;');
                    testDiv.remove();
                }
            });
        } catch (error) {
            console.error('%c✗ GSAP test failed:', 'color:#e74c3c;font-weight:bold;', error);
        }
    }

    // Expose verification function
    window.verifyDependencies = function() {
        console.clear();
        console.log('%c=== Dependency Check ===', 'color:#3498db;font-size:16px;font-weight:bold;');
        Object.entries(checks).forEach(([name, passed]) => {
            console.log(`${name}: ${passed ? '✓ Loaded' : '✗ Not loaded'}`);
        });
    };

})();
