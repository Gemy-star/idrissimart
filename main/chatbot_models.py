"""
Chatbot Models for Idrissimart Helper
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ChatbotKnowledgeBase(models.Model):
    """Knowledge base for chatbot responses"""
    
    class Category(models.TextChoices):
        GENERAL = 'general', _('عام')
        ABOUT = 'about', _('حول الموقع')
        SERVICES = 'services', _('الخدمات')
        ADS = 'ads', _('الإعلانات')
        MARKETPLACE = 'marketplace', _('المتجر')
        COURSES = 'courses', _('الدورات')
        JOBS = 'jobs', _('الوظائف')
        ACCOUNT = 'account', _('الحساب')
        PAYMENT = 'payment', _('الدفع')
        SUPPORT = 'support', _('الدعم الفني')
    
    question = models.TextField(
        verbose_name=_("السؤال"),
        help_text=_("السؤال أو الكلمات المفتاحية")
    )
    answer = models.TextField(
        verbose_name=_("الإجابة"),
        help_text=_("الإجابة التفصيلية")
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name=_("الفئة")
    )
    keywords = models.TextField(
        blank=True,
        verbose_name=_("الكلمات المفتاحية"),
        help_text=_("كلمات مفتاحية مفصولة بفواصل للبحث")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    priority = models.IntegerField(
        default=1,
        verbose_name=_("الأولوية"),
        help_text=_("أولوية عرض الإجابة (الأعلى أولاً)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("قاعدة معرفة الشات بوت")
        verbose_name_plural = _("قاعدة معرفة الشات بوت")
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.question[:50]}..."


class ChatbotConversation(models.Model):
    """Store chatbot conversations"""
    
    session_id = models.CharField(
        max_length=255,
        verbose_name=_("معرف الجلسة")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم")
    )
    user_message = models.TextField(
        verbose_name=_("رسالة المستخدم")
    )
    bot_response = models.TextField(
        verbose_name=_("رد الشات بوت")
    )
    matched_knowledge = models.ForeignKey(
        ChatbotKnowledgeBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المعرفة المطابقة")
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("مفيد")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("محادثة الشات بوت")
        verbose_name_plural = _("محادثات الشات بوت")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"محادثة {self.session_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatbotQuickAction(models.Model):
    """Quick action buttons for chatbot"""
    
    title = models.CharField(
        max_length=100,
        verbose_name=_("العنوان")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("الوصف")
    )
    action_type = models.CharField(
        max_length=50,
        choices=[
            ('message', _('رسالة')),
            ('url', _('رابط')),
            ('search', _('بحث')),
        ],
        default='message',
        verbose_name=_("نوع الإجراء")
    )
    action_value = models.TextField(
        verbose_name=_("قيمة الإجراء"),
        help_text=_("النص أو الرابط أو استعلام البحث")
    )
    icon = models.CharField(
        max_length=50,
        default='fas fa-question',
        verbose_name=_("الأيقونة"),
        help_text=_("فئة CSS للأيقونة")
    )
    order = models.IntegerField(
        default=1,
        verbose_name=_("الترتيب")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    class Meta:
        verbose_name = _("إجراء سريع للشات بوت")
        verbose_name_plural = _("إجراءات سريعة للشات بوت")
        ordering = ['order']
    
    def __str__(self):
        return self.title
