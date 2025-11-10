/**
 * Ad Card Component Interactions
 * Handles animations and user interactions for modern ad cards
 * Depends on: cart-wishlist.js (for CartWishlist global object)
 * Requires: GSAP library
 */

// Ensure GSAP is loaded
if (typeof gsap === 'undefined') {
    console.warn('GSAP library not loaded. Ad card animations will not work.');
}

/**
 * Initialize ad card animations
 */
function initAdCardAnimations() {
    if (typeof gsap === 'undefined') return;

    const cards = document.querySelectorAll('.modern-ad-card');

    cards.forEach((card, index) => {
        // Create timeline for hover animations
        const tl = gsap.timeline({ paused: true });
        const avatar = card.querySelector('.publisher-avatar-simple');
        const avatarBadge = card.querySelector('.avatar-badge');
        const priceSection = card.querySelector('.ad-price-clean');

        // Hover animation sequence
        if (priceSection) {
            tl.to(card, {
                y: -8,
                scale: 1.02,
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
                duration: 0.3,
                ease: 'power2.out'
            });

            if (avatar) {
                tl.to(avatar, {
                    scale: 1.15,
                    rotation: 360,
                    duration: 0.4,
                    ease: 'back.out(1.7)'
                }, 0.1);
            }

            if (avatarBadge) {
                tl.to(avatarBadge, {
                    scale: 1.2,
                    rotation: 5,
                    duration: 0.3,
                    ease: 'elastic.out(1, 0.75)'
                }, 0.2);
            }

            tl.to(priceSection, {
                scale: 1.05,
                duration: 0.3,
                ease: 'power2.out'
            }, 0.1);

            // Add event listeners
            card.addEventListener('mouseenter', () => tl.play());
            card.addEventListener('mouseleave', () => tl.reverse());
        }

        // Initial entrance animation with stagger
        gsap.fromTo(card,
            {
                opacity: 0,
                y: 50,
                scale: 0.9
            },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.6,
                ease: 'back.out(1.7)',
                delay: index * 0.1, // Stagger effect based on index
                scrollTrigger: {
                    trigger: card,
                    start: 'top 90%',
                    once: true
                }
            }
        );
    });
}

/**
 * Share ad functionality
 * @param {number} adId - The ad ID
 * @param {Event} event - The click event
 */
function shareAd(adId, event) {
    event = event || window.event;
    event.preventDefault();

    const adUrl = window.location.origin + '/ad/' + adId;

    if (navigator.share) {
        navigator.share({
            title: 'إعلان مميز',
            text: 'شاهد هذا الإعلان المميز',
            url: adUrl
        }).catch(err => console.log('Share failed:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(adUrl).then(() => {
            showNotification('تم نسخ الرابط');
        }).catch(err => {
            console.error('Failed to copy:', err);
            showNotification('فشل نسخ الرابط');
        });
    }
}

/**
 * Show contact modal
 * @param {number} adId - The ad ID
 * @param {Event} event - The click event
 */
function showContactModal(adId, event) {
    if (event) event.preventDefault();

    // TODO: Implement contact modal
    console.log('Show contact modal for ad:', adId);
}

/**
 * Initiate call to seller
 * @param {number} adId - The ad ID
 * @param {Event} event - The click event
 */
function callSeller(adId, event) {
    if (event) event.preventDefault();

    // TODO: Implement call seller functionality
    console.log('Call seller for ad:', adId);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdCardAnimations);
} else {
    initAdCardAnimations();
}



// Re-initialize on dynamic content load (e.g., AJAX pagination)
window.refreshAdCardAnimations = initAdCardAnimations;
