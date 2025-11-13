"""
Chatbot Views for Idrissimart Helper
"""
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from .chatbot_service import IdrissmartChatbot
from .chatbot_models import ChatbotConversation, ChatbotQuickAction


class ChatbotView(View):
    """Main chatbot interface view"""
    
    def get(self, request):
        """Render chatbot interface"""
        quick_actions = ChatbotQuickAction.objects.filter(is_active=True)[:5]
        
        context = {
            'quick_actions': quick_actions,
            'page_title': 'مساعد إدريسي مارت الذكي'
        }
        
        return render(request, 'chatbot/chat_interface.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_message(request):
    """Handle chatbot message API"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'الرسالة مطلوبة'
            })
        
        # Initialize chatbot
        chatbot = IdrissmartChatbot()
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Get response
        response_data = chatbot.get_response(
            message=message,
            session_id=session_id,
            user=user
        )
        
        # Format quick actions for JSON response
        quick_actions = []
        for action in response_data.get('quick_actions', []):
            quick_actions.append({
                'title': action.title,
                'action_type': action.action_type,
                'action_value': action.action_value,
                'icon': action.icon
            })
        
        return JsonResponse({
            'success': True,
            'response': response_data['response'],
            'session_id': response_data['session_id'],
            'conversation_id': response_data['conversation_id'],
            'quick_actions': quick_actions,
            'suggestions': response_data.get('suggestions', []),
            'timestamp': ChatbotConversation.objects.get(
                id=response_data['conversation_id']
            ).created_at.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'بيانات JSON غير صحيحة'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في الخادم'
        })


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_rate(request):
    """Rate chatbot response"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        is_helpful = data.get('is_helpful')
        
        if conversation_id is None or is_helpful is None:
            return JsonResponse({
                'success': False,
                'error': 'معرف المحادثة والتقييم مطلوبان'
            })
        
        chatbot = IdrissmartChatbot()
        success = chatbot.rate_response(conversation_id, is_helpful)
        
        return JsonResponse({
            'success': success,
            'message': 'شكراً لتقييمك!' if success else 'فشل في حفظ التقييم'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'بيانات JSON غير صحيحة'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في الخادم'
        })


@csrf_exempt
@require_http_methods(["GET"])
def chatbot_history(request):
    """Get conversation history"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return JsonResponse({
            'success': False,
            'error': 'معرف الجلسة مطلوب'
        })
    
    try:
        chatbot = IdrissmartChatbot()
        conversations = chatbot.get_conversation_history(session_id)
        
        history = []
        for conv in conversations:
            history.append({
                'id': conv.id,
                'user_message': conv.user_message,
                'bot_response': conv.bot_response,
                'timestamp': conv.created_at.isoformat(),
                'is_helpful': conv.is_helpful
            })
        
        return JsonResponse({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في جلب التاريخ'
        })


@method_decorator(login_required, name='dispatch')
class ChatbotAdminView(View):
    """Admin view for chatbot management"""
    
    def get(self, request):
        """Display chatbot admin dashboard"""
        if not request.user.is_staff:
            return render(request, '403.html', status=403)
        
        from .chatbot_models import ChatbotKnowledgeBase, ChatbotQuickAction
        
        # Get conversation statistics
        total_conversations = ChatbotConversation.objects.count()
        helpful_responses = ChatbotConversation.objects.filter(
            is_helpful=True
        ).count()
        
        # Get knowledge base count
        knowledge_count = ChatbotKnowledgeBase.objects.filter(is_active=True).count()
        
        # Get recent conversations
        recent_conversations = ChatbotConversation.objects.select_related(
            'user', 'matched_knowledge'
        ).order_by('-created_at')[:10]
        
        # Calculate success rate
        rated_conversations = ChatbotConversation.objects.filter(
            is_helpful__isnull=False
        ).count()
        
        success_rate = 0
        if rated_conversations > 0:
            success_rate = (helpful_responses / rated_conversations) * 100
        
        context = {
            'active_nav': 'chatbot',
            'total_conversations': total_conversations,
            'helpful_responses': helpful_responses,
            'success_rate': round(success_rate, 1),
            'knowledge_count': knowledge_count,
            'recent_conversations': recent_conversations,
            'page_title': 'إدارة الشات بوت'
        }
        
        return render(request, 'chatbot/admin_dashboard.html', context)


def chatbot_widget_data(request):
    """Get data for chatbot widget"""
    from .chatbot_models import ChatbotQuickAction
    quick_actions = ChatbotQuickAction.objects.filter(is_active=True)[:3]
    
    actions_data = []
    for action in quick_actions:
        actions_data.append({
            'title': action.title,
            'action_type': action.action_type,
            'action_value': action.action_value,
            'icon': action.icon
        })
    
    return JsonResponse({
        'success': True,
        'quick_actions': actions_data,
        'greeting': 'مرحباً! كيف يمكنني مساعدتك في إدريسي مارت؟ 👋'
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def manage_knowledge(request):
    """Manage knowledge base entries"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'غير مصرح'})
    
    from .chatbot_models import ChatbotKnowledgeBase
    
    if request.method == 'GET':
        # Get knowledge base entries
        entries = ChatbotKnowledgeBase.objects.all().order_by('-priority', '-created_at')[:20]
        
        data = []
        for entry in entries:
            data.append({
                'id': entry.id,
                'question': entry.question,
                'answer': entry.answer,
                'category': entry.get_category_display(),
                'category_value': entry.category,
                'keywords': entry.keywords,
                'priority': entry.priority,
                'is_active': entry.is_active,
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'entries': data
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            entry = ChatbotKnowledgeBase.objects.create(
                question=data.get('question'),
                answer=data.get('answer'),
                category=data.get('category'),
                keywords=data.get('keywords', ''),
                priority=int(data.get('priority', 1)),
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'تم إضافة المعرفة بنجاح',
                'entry_id': entry.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'خطأ في إضافة المعرفة: {str(e)}'
            })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def manage_actions(request):
    """Manage quick actions"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'غير مصرح'})
    
    from .chatbot_models import ChatbotQuickAction
    
    if request.method == 'GET':
        # Get quick actions
        actions = ChatbotQuickAction.objects.all().order_by('order')
        
        data = []
        for action in actions:
            data.append({
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'action_type': action.get_action_type_display(),
                'action_type_value': action.action_type,
                'action_value': action.action_value,
                'icon': action.icon,
                'order': action.order,
                'is_active': action.is_active
            })
        
        return JsonResponse({
            'success': True,
            'actions': data
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            action = ChatbotQuickAction.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                action_type=data.get('action_type'),
                action_value=data.get('action_value'),
                icon=data.get('icon', 'fas fa-question'),
                order=int(data.get('order', 1)),
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'تم إضافة الإجراء السريع بنجاح',
                'action_id': action.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'خطأ في إضافة الإجراء: {str(e)}'
            })
