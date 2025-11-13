"""
Django Admin configuration for Chatbot models
"""
from django.contrib import admin
from django.utils.html import format_html
from .chatbot_models import ChatbotKnowledgeBase, ChatbotConversation, ChatbotQuickAction


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'category', 'priority', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'priority', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    list_editable = ['priority', 'is_active']
    ordering = ['-priority', '-created_at']
    
    fieldsets = (
        ('المحتوى الأساسي', {
            'fields': ('question', 'answer', 'category')
        }),
        ('إعدادات البحث', {
            'fields': ('keywords', 'priority', 'is_active')
        }),
    )
    
    def question_short(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_short.short_description = 'السؤال'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['session_short', 'user', 'user_message_short', 'helpful_status', 'created_at']
    list_filter = ['is_helpful', 'created_at', 'matched_knowledge__category']
    search_fields = ['session_id', 'user_message', 'bot_response', 'user__username']
    readonly_fields = ['session_id', 'user', 'user_message', 'bot_response', 'matched_knowledge', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات الجلسة', {
            'fields': ('session_id', 'user', 'created_at')
        }),
        ('المحادثة', {
            'fields': ('user_message', 'bot_response', 'matched_knowledge')
        }),
        ('التقييم', {
            'fields': ('is_helpful',)
        }),
    )
    
    def session_short(self, obj):
        return obj.session_id[-8:] if obj.session_id else 'N/A'
    session_short.short_description = 'الجلسة'
    
    def user_message_short(self, obj):
        return obj.user_message[:40] + '...' if len(obj.user_message) > 40 else obj.user_message
    user_message_short.short_description = 'رسالة المستخدم'
    
    def helpful_status(self, obj):
        if obj.is_helpful is None:
            return format_html('<span style="color: gray;">غير مقيم</span>')
        elif obj.is_helpful:
            return format_html('<span style="color: green;">✓ مفيد</span>')
        else:
            return format_html('<span style="color: red;">✗ غير مفيد</span>')
    helpful_status.short_description = 'التقييم'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'matched_knowledge')


@admin.register(ChatbotQuickAction)
class ChatbotQuickActionAdmin(admin.ModelAdmin):
    list_display = ['title', 'action_type', 'icon', 'order', 'is_active']
    list_filter = ['action_type', 'is_active']
    search_fields = ['title', 'description', 'action_value']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    
    fieldsets = (
        ('المحتوى', {
            'fields': ('title', 'description', 'icon')
        }),
        ('الإجراء', {
            'fields': ('action_type', 'action_value')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
