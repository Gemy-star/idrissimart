// Safety Tips Admin JavaScript

(function($) {
    'use strict';

    $(document).ready(function() {
        // Icon class preview
        const iconInput = $('#id_icon_class');
        if (iconInput.length) {
            // Create preview element
            const preview = $('<div class="icon-preview" style="margin-top: 10px;"></div>');
            iconInput.after(preview);

            // Update preview function
            function updateIconPreview() {
                const iconClass = iconInput.val();
                if (iconClass) {
                    preview.html(`
                        <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                            <i class="${iconClass}" style="font-size: 48px; color: #667eea;"></i>
                            <p style="margin-top: 10px; color: #666; font-size: 13px;">معاينة الأيقونة</p>
                        </div>
                    `);
                } else {
                    preview.html('<p style="color: #999;">أدخل class للأيقونة لرؤية المعاينة</p>');
                }
            }

            // Initial preview
            updateIconPreview();

            // Update on input
            iconInput.on('input', updateIconPreview);
        }

        // Color theme preview for select
        const colorSelect = $('#id_color_theme');
        if (colorSelect.length) {
            const colorPreview = $('<div class="color-preview" style="margin-top: 10px;"></div>');
            colorSelect.after(colorPreview);

            const colorMap = {
                'tip-blue': { color: '#2196f3', name: 'أزرق', emoji: '🔵' },
                'tip-green': { color: '#4caf50', name: 'أخضر', emoji: '🟢' },
                'tip-orange': { color: '#ff9800', name: 'برتقالي', emoji: '🟠' },
                'tip-red': { color: '#e91e63', name: 'أحمر', emoji: '🔴' },
                'tip-purple': { color: '#9c27b0', name: 'بنفسجي', emoji: '🟣' },
                'tip-teal': { color: '#009688', name: 'تركواز', emoji: '🔷' }
            };

            function updateColorPreview() {
                const selectedColor = colorSelect.val();
                const colorInfo = colorMap[selectedColor];

                if (colorInfo) {
                    colorPreview.html(`
                        <div style="padding: 15px; background: ${colorInfo.color}; color: white; border-radius: 8px; text-align: center; font-weight: 600;">
                            ${colorInfo.emoji} ${colorInfo.name}
                        </div>
                    `);
                }
            }

            updateColorPreview();
            colorSelect.on('change', updateColorPreview);
        }

        // Add quick tips button in changelist
        if ($('.object-tools').length) {
            const quickTipsBtn = $(`
                <li>
                    <a href="#" id="quick-tips-guide" style="background: #4caf50;">
                        <i class="fas fa-lightbulb"></i> نصائح سريعة
                    </a>
                </li>
            `);
            $('.object-tools').prepend(quickTipsBtn);

            $('#quick-tips-guide').on('click', function(e) {
                e.preventDefault();

                const modal = $(`
                    <div class="quick-tips-modal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px;">
                        <div style="background: white; border-radius: 16px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 30px; position: relative;">
                            <button class="close-modal" style="position: absolute; top: 15px; left: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999;">&times;</button>
                            <h2 style="color: #667eea; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-lightbulb"></i>
                                نصائح لاستخدام نصائح الأمان
                            </h2>
                            <div style="line-height: 1.8; color: #333;">
                                <h3 style="color: #764ba2; margin-top: 20px;">🎯 الأيقونات المقترحة:</h3>
                                <ul style="list-style: none; padding: 0;">
                                    <li style="padding: 8px 0;"><code>fas fa-handshake</code> - للقاء البائع</li>
                                    <li style="padding: 8px 0;"><code>fas fa-search-dollar</code> - لفحص المنتج</li>
                                    <li style="padding: 8px 0;"><code>fas fa-money-bill-wave</code> - للدفع</li>
                                    <li style="padding: 8px 0;"><code>fas fa-exclamation-triangle</code> - للتحذيرات</li>
                                    <li style="padding: 8px 0;"><code>fas fa-shield-alt</code> - للحماية</li>
                                    <li style="padding: 8px 0;"><code>fas fa-user-check</code> - للتحقق</li>
                                </ul>

                                <h3 style="color: #764ba2; margin-top: 20px;">📋 أفضل الممارسات:</h3>
                                <ul>
                                    <li>استخدم عناوين قصيرة وواضحة (3-6 كلمات)</li>
                                    <li>اجعل الوصف مختصراً (10-15 كلمة)</li>
                                    <li>استخدم ألوان مختلفة لنصائح مختلفة</li>
                                    <li>رتب النصائح حسب الأهمية</li>
                                    <li>اترك حقل الفئة فارغاً للنصائح العامة</li>
                                </ul>

                                <h3 style="color: #764ba2; margin-top: 20px;">🎨 توصيات الألوان:</h3>
                                <ul style="list-style: none; padding: 0;">
                                    <li style="padding: 8px 0;">🔵 <strong>أزرق</strong> - معلومات عامة</li>
                                    <li style="padding: 8px 0;">🟢 <strong>أخضر</strong> - نصائح إيجابية</li>
                                    <li style="padding: 8px 0;">🟠 <strong>برتقالي</strong> - تنبيهات</li>
                                    <li style="padding: 8px 0;">🔴 <strong>أحمر</strong> - تحذيرات مهمة</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `);

                $('body').append(modal);

                modal.find('.close-modal').on('click', function() {
                    modal.fadeOut(300, function() {
                        $(this).remove();
                    });
                });

                modal.on('click', function(e) {
                    if ($(e.target).hasClass('quick-tips-modal')) {
                        modal.fadeOut(300, function() {
                            $(this).remove();
                        });
                    }
                });
            });
        }

        // Highlight newly saved object
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('_changelist_filters') || urlParams.has('saved')) {
            setTimeout(function() {
                $('.results tbody tr').first().css({
                    'background': '#e8f5e9',
                    'animation': 'pulse 2s ease-in-out'
                });
            }, 300);
        }
    });
})(django.jQuery);
