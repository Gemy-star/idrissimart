/**
 * Newsletter Subscription Handler
 * Handles AJAX newsletter form submissions
 */

document.addEventListener('DOMContentLoaded', function () {
    const newsletterForm = document.getElementById('newsletterForm');
    const newsletterEmail = document.getElementById('newsletterEmail');
    const newsletterSubmitBtn = document.getElementById('newsletterSubmitBtn');
    const newsletterMessage = document.getElementById('newsletterMessage');

    if (!newsletterForm) {
        return; // Newsletter form not found on this page
    }

    newsletterForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // Get email value
        const email = newsletterEmail.value.trim();

        // Validate email
        if (!email) {
            showMessage(
                'error',
                'يرجى إدخال بريد إلكتروني'
            );
            return;
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showMessage(
                'error',
                'صيغة البريد الإلكتروني غير صحيحة'
            );
            return;
        }

        // Disable submit button and show loading state
        newsletterSubmitBtn.disabled = true;
        const originalButtonText = newsletterSubmitBtn.innerHTML;
        newsletterSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري الإرسال...';

        // Get CSRF token
        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value
            || getCookie('csrftoken');

        // Send AJAX request
        const formData = new FormData();
        formData.append('email', email);

        fetch('/ar/api/newsletter/subscribe/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    showMessage('success', data.message);
                    // Reset form
                    newsletterForm.reset();
                    newsletterEmail.focus();
                } else {
                    showMessage('error', data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                showMessage('error', 'حدث خطأ أثناء الاشتراك. يرجى المحاولة لاحقاً.');
            })
            .finally(() => {
                // Re-enable submit button
                newsletterSubmitBtn.disabled = false;
                newsletterSubmitBtn.innerHTML = originalButtonText;
            });
    });

    /**
     * Show message in the message container
     * @param {string} type - Message type: 'success' or 'error'
     * @param {string} message - Message text
     */
    function showMessage(type, message) {
        newsletterMessage.style.display = 'block';
        newsletterMessage.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        newsletterMessage.innerHTML = message;

        // Auto-hide message after 5 seconds
        setTimeout(() => {
            newsletterMessage.style.display = 'none';
        }, 5000);
    }

    /**
     * Get CSRF token from cookies
     * @param {string} name - Cookie name
     * @returns {string|null} Cookie value
     */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }
});
