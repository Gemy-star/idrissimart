// ===========================
// Cart & Wishlist System - Clean Implementation
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
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    return window.isAuthenticated === true;
}

/**
 * Update header count for cart or wishlist
 */
function updateHeaderCount(type, count) {
    const selectors = {
        'cart': '.cart-count',
        'wishlist': '.wishlist-count'
    };

    const elements = document.querySelectorAll(selectors[type]);
    elements.forEach(element => {
        element.textContent = count;
        // Add animation
        element.style.transform = 'scale(1.3)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    });
}

/**
 * Show notification toast
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
        animation: slideInRight 0.3s ease;
    `;

    notification.innerHTML = `<span style="font-size: 1.2rem;">${icons[type]}</span> ${message}`;
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Add item to cart
 */
async function addToCart(itemId, itemName = 'المنتج') {
    if (!isUserAuthenticated()) {
        showNotification('يجب تسجيل الدخول لإضافة المنتجات للسلة', 'error');
        setTimeout(() => {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }, 1500);
        return { success: false };
    }

    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update both counts if provided
            if (data.cart_count !== undefined) {
                updateHeaderCount('cart', data.cart_count);
            }
            if (data.wishlist_count !== undefined) {
                updateHeaderCount('wishlist', data.wishlist_count);
            }
            showNotification(data.message || `تمت إضافة ${itemName} إلى السلة`, 'success');

            // Dispatch event for other components to listen
            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { action: 'add', itemId, count: data.cart_count }
            }));
        } else {
            showNotification(data.message || 'حدث خطأ', 'error');
        }

        return data;
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        return { success: false, error: error.message };
    }
}

/**
 * Remove item from cart
 */
async function removeFromCart(itemId, itemName = 'المنتج') {
    if (!isUserAuthenticated()) {
        showNotification('يجب تسجيل الدخول', 'error');
        return { success: false };
    }

    try {
        const response = await fetch('/api/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update both counts if provided
            if (data.cart_count !== undefined) {
                updateHeaderCount('cart', data.cart_count);
            }
            if (data.wishlist_count !== undefined) {
                updateHeaderCount('wishlist', data.wishlist_count);
            }
            showNotification(data.message || `تمت إزالة ${itemName} من السلة`, 'success');

            // Dispatch event
            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { action: 'remove', itemId, count: data.cart_count }
            }));
        } else {
            showNotification(data.message || 'حدث خطأ', 'error');
        }

        return data;
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        return { success: false, error: error.message };
    }
}

/**
 * Add item to wishlist
 */
async function addToWishlist(itemId, itemName = 'المنتج') {
    if (!isUserAuthenticated()) {
        showNotification('يجب تسجيل الدخول لإضافة المنتجات للمفضلة', 'error');
        setTimeout(() => {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }, 1500);
        return { success: false };
    }

    try {
        const response = await fetch('/api/wishlist/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update both counts if provided
            if (data.wishlist_count !== undefined) {
                updateHeaderCount('wishlist', data.wishlist_count);
            }
            if (data.cart_count !== undefined) {
                updateHeaderCount('cart', data.cart_count);
            }
            showNotification(data.message || `تمت إضافة ${itemName} إلى المفضلة`, 'success');

            // Dispatch event
            document.dispatchEvent(new CustomEvent('wishlistUpdated', {
                detail: { action: 'add', itemId, count: data.wishlist_count }
            }));
        } else {
            showNotification(data.message || 'حدث خطأ', 'error');
        }

        return data;
    } catch (error) {
        console.error('Error adding to wishlist:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        return { success: false, error: error.message };
    }
}

/**
 * Remove item from wishlist
 */
async function removeFromWishlist(itemId, itemName = 'المنتج') {
    if (!isUserAuthenticated()) {
        showNotification('يجب تسجيل الدخول', 'error');
        return { success: false };
    }

    try {
        const response = await fetch('/api/wishlist/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update both counts if provided
            if (data.wishlist_count !== undefined) {
                updateHeaderCount('wishlist', data.wishlist_count);
            }
            if (data.cart_count !== undefined) {
                updateHeaderCount('cart', data.cart_count);
            }
            showNotification(data.message || `تمت إزالة ${itemName} من المفضلة`, 'success');

            // Dispatch event
            document.dispatchEvent(new CustomEvent('wishlistUpdated', {
                detail: { action: 'remove', itemId, count: data.wishlist_count }
            }));
        } else {
            showNotification(data.message || 'حدث خطأ', 'error');
        }

        return data;
    } catch (error) {
        console.error('Error removing from wishlist:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        return { success: false, error: error.message };
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
 * Sync cart/wishlist button states with database
 * Call this on page load to ensure buttons reflect actual DB state
 */
async function syncButtonStates() {
    if (!isUserAuthenticated()) return;

    // Sync cart buttons - check all possible selectors
    const cartButtons = document.querySelectorAll('button.cart-btn-card[data-ad-id], button.ad-cart-btn[data-ad-id], button.add-to-cart-btn[data-ad-id]');
    cartButtons.forEach(button => {
        const adId = button.dataset.adId;
        if (adId) {
            // Check data-in-cart attribute (from template)
            const isInCart = button.dataset.inCart === 'true';

            // Ensure button state matches database state from template
            if (isInCart) {
                button.classList.add('active');
                button.dataset.inCart = 'true';
                button.title = 'في السلة';
                button.setAttribute('aria-label', 'في السلة');
            } else {
                button.classList.remove('active');
                button.dataset.inCart = 'false';
                button.title = 'إضافة للسلة';
                button.setAttribute('aria-label', 'إضافة للسلة');
            }
        }
    });

    // Sync wishlist buttons - check all possible selectors
    const wishlistButtons = document.querySelectorAll('button.wishlist-btn-card[data-ad-id], button.ad-wishlist-btn[data-ad-id], button.wishlist-btn[data-ad-id]');
    wishlistButtons.forEach(button => {
        const adId = button.dataset.adId;
        if (adId) {
            // Check data-in-wishlist attribute (from template)
            const isInWishlist = button.dataset.inWishlist === 'true';
            const icon = button.querySelector('i');

            // Ensure button state matches database state from template
            if (isInWishlist) {
                button.classList.add('active');
                button.dataset.inWishlist = 'true';
                if (icon) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                }
                button.title = 'في المفضلة';
                button.setAttribute('aria-label', 'في المفضلة');
            } else {
                button.classList.remove('active');
                button.dataset.inWishlist = 'false';
                if (icon) {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                }
                button.title = 'إضافة للمفضلة';
                button.setAttribute('aria-label', 'إضافة للمفضلة');
            }
        }
    });
}

// Event listeners for dynamic content
document.addEventListener('cartUpdated', (e) => {
    console.log('Cart updated:', e.detail);

    // Update all cart buttons for this ad
    const adId = e.detail.itemId;
    const isInCart = e.detail.action === 'add';

    document.querySelectorAll(`[data-ad-id="${adId}"].cart-btn-card, [data-ad-id="${adId}"].ad-cart-btn`).forEach(btn => {
        if (isInCart) {
            btn.classList.add('active');
            btn.title = 'في السلة';
            btn.setAttribute('aria-label', 'في السلة');
        } else {
            btn.classList.remove('active');
            btn.title = 'إضافة للسلة';
            btn.setAttribute('aria-label', 'إضافة للسلة');
        }
    });

    // Refresh cart UI if on cart page
    if (window.location.pathname.includes('/cart/')) {
        location.reload();
    }
});

document.addEventListener('wishlistUpdated', (e) => {
    console.log('Wishlist updated:', e.detail);

    // Update all wishlist buttons for this ad
    const adId = e.detail.itemId;
    const isInWishlist = e.detail.action === 'add';

    document.querySelectorAll(`[data-ad-id="${adId}"].wishlist-btn-card, [data-ad-id="${adId}"].ad-wishlist-btn`).forEach(btn => {
        const icon = btn.querySelector('i');
        if (isInWishlist) {
            btn.classList.add('active');
            if (icon) {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }
            btn.title = 'في المفضلة';
            btn.setAttribute('aria-label', 'في المفضلة');
        } else {
            btn.classList.remove('active');
            if (icon) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
            btn.title = 'إضافة للمفضلة';
            btn.setAttribute('aria-label', 'إضافة للمفضلة');
        }
    });

    // Refresh wishlist UI if on wishlist page
    if (window.location.pathname.includes('/wishlist/')) {
        location.reload();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', syncButtonStates);

/**
 * Toggle cart button (add/remove from cart)
 */
async function toggleCartCard(adId, button, itemName = 'المنتج', price = 0) {
    // Check data attribute first, fallback to class
    const isInCart = button.dataset.inCart === 'true' || button.classList.contains('active');

    // Disable button during request
    button.disabled = true;

    try {
        let result;
        if (isInCart) {
            result = await removeFromCart(adId, itemName);
        } else {
            result = await addToCart(adId, itemName);
        }

        if (result && result.success) {
            const newState = !isInCart;

            // Update all cart buttons for this ad (in case there are multiple)
            const allCartButtons = document.querySelectorAll(`button.cart-btn-card[data-ad-id="${adId}"], button.ad-cart-btn[data-ad-id="${adId}"], button.add-to-cart-btn[data-ad-id="${adId}"]`);
            allCartButtons.forEach(btn => {
                if (newState) {
                    // Added to cart
                    btn.classList.add('active');
                    btn.dataset.inCart = 'true';
                    if (btn.dataset.isInCart !== undefined) {
                        btn.dataset.isInCart = 'true';
                    }
                    btn.title = 'في السلة';
                    btn.setAttribute('aria-label', 'في السلة');

                    // Update button text if it has .button-text span
                    const buttonText = btn.querySelector('.button-text');
                    if (buttonText) {
                        buttonText.textContent = 'إزالة من السلة';
                    }
                } else {
                    // Removed from cart
                    btn.classList.remove('active');
                    btn.dataset.inCart = 'false';
                    if (btn.dataset.isInCart !== undefined) {
                        btn.dataset.isInCart = 'false';
                    }
                    btn.title = 'إضافة للسلة';
                    btn.setAttribute('aria-label', 'إضافة للسلة');

                    // Update button text if it has .button-text span
                    const buttonText = btn.querySelector('.button-text');
                    if (buttonText) {
                        buttonText.textContent = 'إضافة للسلة';
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error toggling cart:', error);
    } finally {
        button.disabled = false;
    }
}

/**
 * Toggle wishlist button (add/remove from wishlist)
 */
async function toggleWishlistCard(adId, button, itemName = 'المنتج') {
    // Check data attribute first, fallback to class
    const isInWishlist = button.dataset.inWishlist === 'true' || button.classList.contains('active');
    const icon = button.querySelector('i');

    // Disable button during request
    button.disabled = true;

    try {
        let result;
        if (isInWishlist) {
            result = await removeFromWishlist(adId, itemName);
        } else {
            result = await addToWishlist(adId, itemName);
        }

        if (result && result.success) {
            const newState = !isInWishlist;

            // Update all wishlist buttons for this ad (in case there are multiple)
            const allWishlistButtons = document.querySelectorAll(`button.wishlist-btn-card[data-ad-id="${adId}"], button.ad-wishlist-btn[data-ad-id="${adId}"], button.wishlist-btn[data-ad-id="${adId}"]`);
            allWishlistButtons.forEach(btn => {
                const btnIcon = btn.querySelector('i');
                if (newState) {
                    // Added to wishlist
                    btn.classList.add('active');
                    btn.dataset.inWishlist = 'true';
                    if (btn.dataset.isInWishlist !== undefined) {
                        btn.dataset.isInWishlist = 'true';
                    }
                    if (btnIcon) {
                        btnIcon.classList.remove('far');
                        btnIcon.classList.add('fas');
                    }
                    btn.title = 'في المفضلة';
                    btn.setAttribute('aria-label', 'في المفضلة');

                    // Update button text if it has .button-text span
                    const buttonText = btn.querySelector('.button-text');
                    if (buttonText) {
                        buttonText.textContent = 'إزالة من المفضلة';
                    }
                } else {
                    // Removed from wishlist
                    btn.classList.remove('active');
                    btn.dataset.inWishlist = 'false';
                    if (btn.dataset.isInWishlist !== undefined) {
                        btn.dataset.isInWishlist = 'false';
                    }
                    if (btnIcon) {
                        btnIcon.classList.remove('fas');
                        btnIcon.classList.add('far');
                    }
                    btn.title = 'إضافة للمفضلة';
                    btn.setAttribute('aria-label', 'إضافة للمفضلة');

                    // Update button text if it has .button-text span
                    const buttonText = btn.querySelector('.button-text');
                    if (buttonText) {
                        buttonText.textContent = 'إضافة للمفضلة';
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error toggling wishlist:', error);
    } finally {
        button.disabled = false;
    }
}

// Make functions globally available
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.addToWishlist = addToWishlist;
window.removeFromWishlist = removeFromWishlist;
window.toggleCartCard = toggleCartCard;
window.toggleWishlistCard = toggleWishlistCard;
window.showNotification = showNotification;
window.updateHeaderCount = updateHeaderCount;
window.syncButtonStates = syncButtonStates;

// Aliases for compatibility
window.updateCartCountInHeader = (count) => updateHeaderCount('cart', count);
window.updateWishlistCountInHeader = (count) => updateHeaderCount('wishlist', count);

/**
 * Fetch current cart and wishlist counts from server
 * Useful for ensuring counts are in sync with database
 */
async function refreshCountsFromServer() {
    if (!isUserAuthenticated()) return;

    try {
        // Fetch cart count
        const cartResponse = await fetch('/api/cart/count/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        if (cartResponse.ok) {
            const cartData = await cartResponse.json();
            if (cartData.success && cartData.cart_count !== undefined) {
                updateHeaderCount('cart', cartData.cart_count);
            }
        }

        // Fetch wishlist count
        const wishlistResponse = await fetch('/api/wishlist/count/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        if (wishlistResponse.ok) {
            const wishlistData = await wishlistResponse.json();
            if (wishlistData.success && wishlistData.wishlist_count !== undefined) {
                updateHeaderCount('wishlist', wishlistData.wishlist_count);
            }
        }
    } catch (error) {
        console.error('Error refreshing counts from server:', error);
    }
}

window.refreshCountsFromServer = refreshCountsFromServer;

