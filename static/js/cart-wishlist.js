// ===========================
// Cart & Wishlist Helper Functions with AJAX
// FILE: static/js/cart-wishlist.js
// ===========================

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * Update badge count with animation
 */
function updateBadgeCount(type, count) {
    const badge = document.querySelector(`.${type}-count`);
    if (badge) {
        // Animate the badge with GSAP if available
        if (typeof gsap !== 'undefined') {
            gsap.to(badge, {
                scale: 1.5,
                duration: 0.2,
                onComplete: () => {
                    badge.textContent = count;
                    gsap.to(badge, {
                        scale: 1,
                        duration: 0.2
                    });
                }
            });
        } else {
            // Fallback animation
            badge.style.transform = 'scale(1.5)';
            badge.textContent = count;
            setTimeout(() => {
                badge.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

/**
 * Show notification with custom message
 */
function showNotification(message, type = 'success') {
    const colors = {
        success: 'linear-gradient(135deg, #4B315E 0%, #6B4C7A 100%)',
        error: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
        info: 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)'
    };

    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ'
    };

    const notification = document.createElement('div');
    notification.className = 'custom-notification';
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 350px;
    `;

    notification.innerHTML = `<span style="font-size: 1.2rem;">${icons[type]}</span> ${message}`;

    document.body.appendChild(notification);

    // Animate in
    if (typeof gsap !== 'undefined') {
        gsap.from(notification, {
            x: 400,
            opacity: 0,
            duration: 0.3,
            ease: 'back.out(1.7)'
        });

        // Animate out and remove
        setTimeout(() => {
            gsap.to(notification, {
                x: 400,
                opacity: 0,
                duration: 0.3,
                onComplete: () => notification.remove()
            });
        }, 3000);
    } else {
        // Fallback animation
        notification.style.animation = 'slideInRight 0.3s ease';
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

/**
 * Add item to cart with AJAX
 */
async function addToCart(itemId, itemName = 'المنتج') {
    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        const data = await response.json();

        if (data.success) {
            updateBadgeCount('cart', data.cart_count);
            showNotification(`✓ تمت إضافة ${itemName} إلى السلة`, 'success');

            // Trigger custom event
            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { count: data.cart_count, itemId: itemId }
            }));
        } else {
            showNotification(`✗ ${data.message}`, 'error');
        }

        return data;
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('✗ حدث خطأ في إضافة المنتج', 'error');
        return { success: false };
    }
}

/**
 * Remove item from cart with AJAX
 */
async function removeFromCart(itemId, itemName = 'المنتج') {
    try {
        const response = await fetch('/api/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        const data = await response.json();

        if (data.success) {
            updateBadgeCount('cart', data.cart_count);
            showNotification(`✓ تمت إزالة ${itemName} من السلة`, 'success');

            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { count: data.cart_count, itemId: itemId }
            }));
        } else {
            showNotification(`✗ ${data.message}`, 'error');
        }

        return data;
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('✗ حدث خطأ في إزالة المنتج', 'error');
        return { success: false };
    }
}

/**
 * Add item to wishlist with AJAX
 */
async function addToWishlist(itemId, itemName = 'المنتج') {
    try {
        const response = await fetch('/api/wishlist/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        const data = await response.json();

        if (data.success) {
            updateBadgeCount('wishlist', data.wishlist_count);
            showNotification(`✓ تمت إضافة ${itemName} إلى المفضلة`, 'success');

            document.dispatchEvent(new CustomEvent('wishlistUpdated', {
                detail: { count: data.wishlist_count, itemId: itemId }
            }));
        } else {
            showNotification(`✗ ${data.message}`, 'error');
        }

        return data;
    } catch (error) {
        console.error('Error adding to wishlist:', error);
        showNotification('✗ حدث خطأ في إضافة المنتج', 'error');
        return { success: false };
    }
}

/**
 * Remove item from wishlist with AJAX
 */
async function removeFromWishlist(itemId, itemName = 'المنتج') {
    try {
        const response = await fetch('/api/wishlist/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        const data = await response.json();

        if (data.success) {
            updateBadgeCount('wishlist', data.wishlist_count);
            showNotification(`✓ تمت إزالة ${itemName} من المفضلة`, 'success');

            document.dispatchEvent(new CustomEvent('wishlistUpdated', {
                detail: { count: data.wishlist_count, itemId: itemId }
            }));
        } else {
            showNotification(`✗ ${data.message}`, 'error');
        }

        return data;
    } catch (error) {
        console.error('Error removing from wishlist:', error);
        showNotification('✗ حدث خطأ في إزالة المنتج', 'error');
        return { success: false };
    }
}

/**
 * Toggle wishlist button state
 */
function toggleWishlistButton(button, isInWishlist) {
    const icon = button.querySelector('i');
    if (isInWishlist) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        button.classList.add('active');
        button.style.color = '#ff4757';
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        button.classList.remove('active');
        button.style.color = '';
    }
}

/**
 * Initialize cart and wishlist buttons
 */
function initializeCartWishlistButtons() {
    // Cart buttons
    document.querySelectorAll('[data-action="add-to-cart"]').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName || 'المنتج';

            // Add loading state
            this.disabled = true;
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            await addToCart(itemId, itemName);

            // Remove loading state
            this.disabled = false;
            this.innerHTML = originalHTML;
        });
    });

    // Wishlist buttons
    document.querySelectorAll('[data-action="toggle-wishlist"]').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName || 'المنتج';
            const isInWishlist = this.classList.contains('active');

            // Add animation
            if (typeof gsap !== 'undefined') {
                gsap.to(button, {
                    scale: 1.3,
                    duration: 0.2,
                    yoyo: true,
                    repeat: 1
                });
            }

            if (isInWishlist) {
                const result = await removeFromWishlist(itemId, itemName);
                if (result.success) {
                    toggleWishlistButton(button, false);
                }
            } else {
                const result = await addToWishlist(itemId, itemName);
                if (result.success) {
                    toggleWishlistButton(button, true);
                }
            }
        });
    });
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCartWishlistButtons);
} else {
    initializeCartWishlistButtons();
}

// Listen for custom events
document.addEventListener('cartUpdated', (e) => {
    console.log('Cart updated:', e.detail);
});

document.addEventListener('wishlistUpdated', (e) => {
    console.log('Wishlist updated:', e.detail);
});

// Export functions for global use
window.CartWishlist = {
    addToCart,
    removeFromCart,
    addToWishlist,
    removeFromWishlist,
    updateBadgeCount,
    showNotification
};
