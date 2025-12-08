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
            updateHeaderCount('cart', data.cart_count);
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
            updateHeaderCount('cart', data.cart_count);
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
            updateHeaderCount('wishlist', data.wishlist_count);
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
            updateHeaderCount('wishlist', data.wishlist_count);
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

// Event listeners for dynamic content
document.addEventListener('cartUpdated', (e) => {
    console.log('Cart updated:', e.detail);
    // Refresh cart UI if on cart page
    if (window.location.pathname.includes('/cart/')) {
        location.reload();
    }
});

document.addEventListener('wishlistUpdated', (e) => {
    console.log('Wishlist updated:', e.detail);
    // Refresh wishlist UI if on wishlist page
    if (window.location.pathname.includes('/wishlist/')) {
        location.reload();
    }
});

/**
 * Toggle cart button (add/remove from cart)
 */
async function toggleCartCard(adId, button, itemName = 'المنتج', price = 0) {
    const isInCart = button.classList.contains('active');

    if (isInCart) {
        const result = await removeFromCart(adId, itemName);
        if (result.success) {
            button.classList.remove('active');
            button.title = 'إضافة للسلة';
            button.setAttribute('aria-label', 'إضافة للسلة');
        }
    } else {
        const result = await addToCart(adId, itemName);
        if (result.success) {
            button.classList.add('active');
            button.title = 'في السلة';
            button.setAttribute('aria-label', 'في السلة');
        }
    }
}

/**
 * Toggle wishlist button (add/remove from wishlist)
 */
async function toggleWishlistCard(adId, button, itemName = 'المنتج') {
    const isInWishlist = button.classList.contains('active');
    const icon = button.querySelector('i');

    if (isInWishlist) {
        const result = await removeFromWishlist(adId, itemName);
        if (result.success) {
            button.classList.remove('active');
            if (icon) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
            button.title = 'إضافة للمفضلة';
            button.setAttribute('aria-label', 'إضافة للمفضلة');
        }
    } else {
        const result = await addToWishlist(adId, itemName);
        if (result.success) {
            button.classList.add('active');
            if (icon) {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }
            button.title = 'في المفضلة';
            button.setAttribute('aria-label', 'في المفضلة');
        }
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

