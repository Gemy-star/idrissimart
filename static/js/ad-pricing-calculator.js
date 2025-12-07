/**
 * Ad Pricing and Upgrades Calculator
 * حساب تكلفة الإعلان والميزات الإضافية
 */

class AdPricingCalculator {
    constructor() {
        this.basePriceInput = document.getElementById('base_price');
        this.upgrades = {
            highlighted: {
                checkbox: document.getElementById('upgrade_highlighted'),
                price: parseFloat(document.getElementById('upgrade_highlighted')?.dataset.price || 50),
                duration: parseInt(document.getElementById('upgrade_highlighted')?.dataset.duration || 30)
            },
            urgent: {
                checkbox: document.getElementById('upgrade_urgent'),
                price: parseFloat(document.getElementById('upgrade_urgent')?.dataset.price || 30),
                duration: parseInt(document.getElementById('upgrade_urgent')?.dataset.duration || 7)
            },
            pinned: {
                checkbox: document.getElementById('upgrade_pinned'),
                price: parseFloat(document.getElementById('upgrade_pinned')?.dataset.price || 100),
                duration: parseInt(document.getElementById('upgrade_pinned')?.dataset.duration || 30)
            }
        };

        this.totalCostElement = document.getElementById('totalCost');
        this.basePrice = 0;
        this.userHasPackage = document.getElementById('user_has_package')?.value === 'true';

        this.init();
    }

    init() {
        // Initialize base price
        if (this.basePriceInput) {
            this.basePrice = parseFloat(this.basePriceInput.value || 0);
        }

        // Add event listeners
        Object.values(this.upgrades).forEach(upgrade => {
            if (upgrade.checkbox) {
                upgrade.checkbox.addEventListener('change', () => this.calculate());
            }
        });

        // Initial calculation
        this.calculate();
        this.updateUI();
    }

    calculate() {
        let total = 0;

        // Base price (free if user has package)
        if (!this.userHasPackage) {
            total += this.basePrice;
        }

        // Add upgrade costs
        Object.values(this.upgrades).forEach(upgrade => {
            if (upgrade.checkbox && upgrade.checkbox.checked) {
                total += upgrade.price;
            }
        });

        // Update display
        if (this.totalCostElement) {
            this.totalCostElement.textContent = total.toFixed(2);
        }

        // Update hidden input for form submission
        const totalInput = document.getElementById('total_features_price');
        if (totalInput) {
            totalInput.value = total;
        }

        this.updateUI();

        return total;
    }

    updateUI() {
        // Update upgrade option cards appearance
        Object.entries(this.upgrades).forEach(([key, upgrade]) => {
            if (upgrade.checkbox) {
                const card = upgrade.checkbox.closest('.pricing-option');
                if (card) {
                    if (upgrade.checkbox.checked) {
                        card.classList.add('selected');
                    } else {
                        card.classList.remove('selected');
                    }
                }
            }
        });

        // Update package recommendation
        this.updatePackageRecommendation();
    }

    updatePackageRecommendation() {
        const total = this.calculate();
        const packageRecommendation = document.getElementById('package_recommendation');

        if (packageRecommendation && total > 100) {
            packageRecommendation.style.display = 'block';
            packageRecommendation.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-lightbulb me-2"></i>
                    <strong>نصيحة:</strong> بهذه التكلفة، قد توفر أكثر بشراء باقة كاملة!
                    <a href="${packageRecommendation.dataset.packagesUrl}" class="alert-link">
                        عرض الباقات المتاحة
                    </a>
                </div>
            `;
        } else if (packageRecommendation) {
            packageRecommendation.style.display = 'none';
        }
    }

    getSelectedUpgrades() {
        const selected = [];
        Object.entries(this.upgrades).forEach(([key, upgrade]) => {
            if (upgrade.checkbox && upgrade.checkbox.checked) {
                selected.push({
                    type: key,
                    price: upgrade.price,
                    duration: upgrade.duration
                });
            }
        });
        return selected;
    }

    showPreview() {
        const selectedUpgrades = this.getSelectedUpgrades();
        const previewContainer = document.getElementById('ad_preview_upgrades');

        if (!previewContainer) return;

        let html = '<div class="upgrade-preview-badges">';

        selectedUpgrades.forEach(upgrade => {
            let icon, text, className;
            switch(upgrade.type) {
                case 'highlighted':
                    icon = 'fa-star';
                    text = 'مميز';
                    className = 'highlighted';
                    break;
                case 'urgent':
                    icon = 'fa-bolt';
                    text = 'عاجل';
                    className = 'urgent';
                    break;
                case 'pinned':
                    icon = 'fa-thumbtack';
                    text = 'مثبت';
                    className = 'pinned';
                    break;
            }

            html += `
                <span class="ad-badge-overlay ${className}">
                    <i class="fas ${icon}"></i> ${text}
                </span>
            `;
        });

        html += '</div>';
        previewContainer.innerHTML = html;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const pricingCalculator = new AdPricingCalculator();

    // Make it globally accessible
    window.adPricingCalculator = pricingCalculator;

    // Draft save functionality
    const saveDraftBtn = document.getElementById('saveDraftBtn');
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Set status to draft
            const statusInput = document.getElementById('ad_status');
            if (statusInput) {
                statusInput.value = 'draft';
            }

            // Submit form
            const form = document.getElementById('adForm');
            if (form) {
                // Show confirmation
                if (confirm('هل تريد حفظ الإعلان كمسودة؟ يمكنك العودة لإكماله لاحقاً.')) {
                    form.submit();
                }
            }
        });
    }

    // Publish with upgrades functionality
    const publishBtn = document.getElementById('publishWithUpgradesBtn');
    if (publishBtn) {
        publishBtn.addEventListener('click', function(e) {
            const total = pricingCalculator.calculate();
            const selectedUpgrades = pricingCalculator.getSelectedUpgrades();

            if (total > 0 && selectedUpgrades.length > 0) {
                const confirmMsg = `
                    سيتم نشر إعلانك مع المميزات التالية:
                    ${selectedUpgrades.map(u => `• ${u.type === 'highlighted' ? 'مميز' : u.type === 'urgent' ? 'عاجل' : 'مثبت'}`).join('\n')}

                    التكلفة الإجمالية: ${total} ج.م

                    هل تريد المتابعة؟
                `;

                if (!confirm(confirmMsg)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // Real-time preview update
    document.querySelectorAll('[id^="upgrade_"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            pricingCalculator.showPreview();
        });
    });
});

// Package comparison helper
function compareWithPackages(currentCost) {
    fetch('/api/packages/compare?cost=' + currentCost)
        .then(response => response.json())
        .then(data => {
            if (data.better_packages && data.better_packages.length > 0) {
                showPackageComparisonModal(data.better_packages);
            }
        })
        .catch(error => console.error('Error comparing packages:', error));
}

function showPackageComparisonModal(packages) {
    // Implementation for showing modal with package comparison
    // This would show packages that offer better value
    console.log('Better packages available:', packages);
}
