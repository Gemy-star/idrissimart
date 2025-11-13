"""
Chatbot Service for Idrissimart Helper
"""
import re
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .chatbot_models import ChatbotKnowledgeBase, ChatbotConversation, ChatbotQuickAction


class IdrissmartChatbot:
    """Main chatbot service class"""
    
    def __init__(self):
        self.default_responses = {
            'greeting': [
                "مرحباً بك في إدريسي مارت! 👋 كيف يمكنني مساعدتك اليوم؟",
                "أهلاً وسهلاً! أنا مساعد إدريسي مارت الذكي، كيف يمكنني خدمتك؟",
                "مرحباً! أنا هنا لمساعدتك في أي استفسار حول منصة إدريسي مارت."
            ],
            'thanks': [
                "عفواً! سعيد لأنني استطعت مساعدتك 😊",
                "لا شكر على واجب! هل تحتاج لأي مساعدة أخرى؟",
                "أهلاً وسهلاً! أتمنى أن تكون المعلومات مفيدة."
            ],
            'goodbye': [
                "وداعاً! نتطلع لرؤيتك مرة أخرى في إدريسي مارت 👋",
                "إلى اللقاء! لا تتردد في العودة إذا احتجت أي مساعدة.",
                "مع السلامة! أتمنى لك تجربة رائعة في منصتنا."
            ],
            'default': [
                "عذراً، لم أفهم سؤالك تماماً. هل يمكنك إعادة صياغته؟",
                "أعتذر، لا أملك معلومات كافية حول هذا الموضوع. يمكنك التواصل مع فريق الدعم للمساعدة.",
                "لم أتمكن من العثور على إجابة مناسبة. جرب استخدام كلمات مختلفة أو اختر من الأسئلة الشائعة."
            ]
        }
        
        # Keywords for different response types
        self.greeting_keywords = ['مرحبا', 'أهلا', 'سلام', 'هلا', 'مساء الخير', 'صباح الخير', 'hello', 'hi']
        self.thanks_keywords = ['شكرا', 'شكراً', 'مشكور', 'thanks', 'thank you']
        self.goodbye_keywords = ['وداعا', 'وداعاً', 'مع السلامة', 'bye', 'goodbye']
    
    def generate_session_id(self):
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    def preprocess_message(self, message):
        """Clean and preprocess user message"""
        # Remove extra spaces and convert to lowercase
        message = re.sub(r'\s+', ' ', message.strip().lower())
        
        # Remove punctuation except Arabic punctuation
        message = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', ' ', message)
        
        return message
    
    def detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in self.greeting_keywords):
            return 'greeting'
        elif any(keyword in message_lower for keyword in self.thanks_keywords):
            return 'thanks'
        elif any(keyword in message_lower for keyword in self.goodbye_keywords):
            return 'goodbye'
        else:
            return 'question'
    
    def search_knowledge_base(self, message):
        """Search knowledge base for relevant answers"""
        # Preprocess message
        clean_message = self.preprocess_message(message)
        
        # Search in questions and keywords
        results = ChatbotKnowledgeBase.objects.filter(
            Q(question__icontains=clean_message) |
            Q(keywords__icontains=clean_message) |
            Q(answer__icontains=clean_message),
            is_active=True
        ).order_by('-priority', '-created_at')
        
        if results.exists():
            return results.first()
        
        # Try word-by-word search
        words = clean_message.split()
        for word in words:
            if len(word) > 2:  # Skip very short words
                results = ChatbotKnowledgeBase.objects.filter(
                    Q(question__icontains=word) |
                    Q(keywords__icontains=word),
                    is_active=True
                ).order_by('-priority', '-created_at')
                
                if results.exists():
                    return results.first()
        
        return None
    
    def get_response(self, message, session_id=None, user=None):
        """Get chatbot response for user message"""
        if not session_id:
            session_id = self.generate_session_id()
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Handle different intents
        if intent in ['greeting', 'thanks', 'goodbye']:
            import random
            response = random.choice(self.default_responses[intent])
            matched_knowledge = None
        else:
            # Search knowledge base
            matched_knowledge = self.search_knowledge_base(message)
            
            if matched_knowledge:
                response = matched_knowledge.answer
            else:
                import random
                response = random.choice(self.default_responses['default'])
        
        # Add suggestions to every response
        suggestions = self.get_suggestions(intent, matched_knowledge, message)
        if suggestions:
            response += f"\n\n{suggestions}"
        
        # Save conversation
        conversation = ChatbotConversation.objects.create(
            session_id=session_id,
            user=user,
            user_message=message,
            bot_response=response,
            matched_knowledge=matched_knowledge
        )
        
        return {
            'response': response,
            'session_id': session_id,
            'conversation_id': conversation.id,
            'matched_knowledge': matched_knowledge,
            'quick_actions': self.get_quick_actions(intent, matched_knowledge),
            'suggestions': self.get_text_suggestions(intent, matched_knowledge, message)
        }
    
    def get_quick_actions(self, intent, matched_knowledge=None):
        """Get relevant quick action buttons"""
        actions = []
        
        # Get active quick actions
        quick_actions = ChatbotQuickAction.objects.filter(is_active=True)
        
        if intent == 'greeting':
            # Show most common actions for new users
            actions = quick_actions.filter(
                action_type__in=['message', 'url']
            )[:4]
        elif matched_knowledge:
            # Show category-related actions
            category_actions = quick_actions.filter(
                action_value__icontains=matched_knowledge.category
            )[:3]
            actions.extend(category_actions)
        
        # Always include some general actions
        general_actions = quick_actions.filter(
            action_type='message'
        ).exclude(
            id__in=[action.id for action in actions]
        )[:2]
        actions.extend(general_actions)
        
        return actions[:5]  # Limit to 5 actions
    
    def get_suggestions(self, intent, matched_knowledge=None, message=""):
        """Get contextual suggestions based on response"""
        suggestions = []
        
        if intent == 'greeting':
            suggestions = [
                "💡 يمكنك سؤالي عن:",
                "• كيفية إنشاء حساب جديد",
                "• طريقة نشر إعلان",
                "• أنواع الخدمات المتاحة",
                "• طرق الدفع المقبولة"
            ]
        elif intent == 'thanks':
            suggestions = [
                "💡 هل تحتاج مساعدة في:",
                "• البحث عن منتجات معينة",
                "• التواصل مع البائعين",
                "• إدارة حسابك الشخصي"
            ]
        elif intent == 'goodbye':
            suggestions = [
                "💡 قبل المغادرة، تذكر:",
                "• حفظ الإعلانات المفضلة",
                "• متابعة الإشعارات الجديدة",
                "• زيارة قسم العروض الخاصة"
            ]
        elif matched_knowledge:
            # Category-based suggestions
            if matched_knowledge.category == 'ads':
                suggestions = [
                    "💡 مواضيع ذات صلة:",
                    "• كيفية تحسين إعلانك",
                    "• إضافة صور جذابة",
                    "• تحديد السعر المناسب",
                    "• ترقية الإعلان للظهور أكثر"
                ]
            elif matched_knowledge.category == 'account':
                suggestions = [
                    "💡 إدارة الحساب:",
                    "• تحديث البيانات الشخصية",
                    "• تفعيل التحقق من الهوية",
                    "• إعدادات الخصوصية",
                    "• تغيير كلمة المرور"
                ]
            elif matched_knowledge.category == 'payment':
                suggestions = [
                    "💡 المدفوعات والأمان:",
                    "• طرق الدفع الآمنة",
                    "• حماية بياناتك المالية",
                    "• استرداد الأموال",
                    "• فواتير المشتريات"
                ]
            elif matched_knowledge.category == 'services':
                suggestions = [
                    "💡 الخدمات المتاحة:",
                    "• طلب خدمة مخصصة",
                    "• تقييم مقدمي الخدمات",
                    "• متابعة حالة الطلب",
                    "• الدعم الفني"
                ]
            else:
                suggestions = [
                    "💡 مواضيع قد تهمك:",
                    "• الأسئلة الشائعة",
                    "• دليل المستخدم",
                    "• التواصل مع الدعم",
                    "• آخر التحديثات"
                ]
        else:
            # Default suggestions for unmatched queries
            suggestions = [
                "💡 جرب البحث عن:",
                "• كيفية استخدام الموقع",
                "• إنشاء حساب جديد",
                "• نشر إعلان مجاني",
                "• التواصل مع البائعين",
                "• طرق الدفع المتاحة"
            ]
        
        return "\n".join(suggestions) if suggestions else ""
    
    def get_text_suggestions(self, intent, matched_knowledge=None, message=""):
        """Get text-based suggestions for quick replies"""
        if intent == 'greeting':
            return [
                "كيف أنشئ حساب؟",
                "ما هي الخدمات المتاحة؟",
                "كيف أنشر إعلان؟",
                "طرق الدفع المقبولة"
            ]
        elif matched_knowledge:
            if matched_knowledge.category == 'ads':
                return [
                    "كيف أحسن إعلاني؟",
                    "إضافة صور للإعلان",
                    "ترقية الإعلان",
                    "حذف إعلان قديم"
                ]
            elif matched_knowledge.category == 'account':
                return [
                    "تحديث البيانات",
                    "تفعيل الحساب",
                    "تغيير كلمة المرور",
                    "حذف الحساب"
                ]
            elif matched_knowledge.category == 'payment':
                return [
                    "طرق الدفع الآمنة",
                    "استرداد الأموال",
                    "مشاكل الدفع",
                    "فواتير المشتريات"
                ]
        
        return [
            "الأسئلة الشائعة",
            "التواصل مع الدعم",
            "دليل الاستخدام",
            "إبلاغ عن مشكلة"
        ]
    
    def rate_response(self, conversation_id, is_helpful):
        """Rate chatbot response"""
        try:
            conversation = ChatbotConversation.objects.get(id=conversation_id)
            conversation.is_helpful = is_helpful
            conversation.save()
            return True
        except ChatbotConversation.DoesNotExist:
            return False
    
    def get_conversation_history(self, session_id, limit=10):
        """Get conversation history for session"""
        return ChatbotConversation.objects.filter(
            session_id=session_id
        ).order_by('-created_at')[:limit]


def initialize_knowledge_base():
    """Initialize chatbot knowledge base with Idrissimart content"""
    
    knowledge_data = [
        # About Idrissimart
        {
            'question': 'ما هو إدريسي مارت؟',
            'answer': '''إدريسي مارت هي منصة متكاملة تجمع جميع خدمات السوق في مكان واحد، مصممة خصيصاً لتلبية احتياجات المتخصصين والجمهور العام على حد سواء.

نقدم حلولاً شاملة تشمل:
🔸 الإعلانات المبوبة
🔸 المتجر متعدد التجار  
🔸 طلب الخدمات
🔸 الدورات التدريبية
🔸 الفرص الوظيفية

نسعى لخلق تجربة مستخدم فريدة تجمع بين السهولة والكفاءة، مع ضمان أعلى مستويات الجودة والموثوقية.''',
            'category': 'about',
            'keywords': 'إدريسي مارت, منصة, خدمات, السوق, about, idrissimart',
            'priority': 10
        },
        
        # Vision
        {
            'question': 'ما هي رؤية إدريسي مارت؟',
            'answer': '''رؤيتنا هي أن نكون المنصة الرائدة التي تجمع جميع خدمات السوق في مكان واحد، موفرة تجربة متكاملة للمتخصصين والجمهور العام على حد سواء، من خلال تقديم حلول مبتكرة وموثوقة في الإعلانات المبوبة والتجارة الإلكترونية والخدمات التدريبية.''',
            'category': 'about',
            'keywords': 'رؤية, vision, هدف, مستقبل',
            'priority': 8
        },
        
        # Mission
        {
            'question': 'ما هي مهمة إدريسي مارت؟',
            'answer': '''مهمتنا هي توفير منصة متكاملة تجمع جميع خدمات السوق في مكان واحد، مع ضمان سهولة الوصول والاستخدام للجميع، وتقديم خدمات عالية الجودة في:

✅ الإعلانات المبوبة
✅ المتجر متعدد التجار
✅ طلب الخدمات  
✅ الدورات التدريبية
✅ الفرص الوظيفية

كل ذلك بكفاءة وفعالية عالية.''',
            'category': 'about',
            'keywords': 'مهمة, mission, هدف, خدمات',
            'priority': 8
        },
        
        # Services - Classified Ads
        {
            'question': 'كيف أنشر إعلان مبوب؟',
            'answer': '''لنشر إعلان مبوب في إدريسي مارت:

1️⃣ سجل الدخول إلى حسابك
2️⃣ اضغط على "إنشاء إعلان جديد"
3️⃣ اختر القسم المناسب
4️⃣ املأ تفاصيل الإعلان (العنوان، الوصف، السعر)
5️⃣ أضف الصور (حتى 5 صور)
6️⃣ تحقق من رقم الجوال عبر OTP
7️⃣ اضغط "نشر الإعلان"

سيتم مراجعة إعلانك وتفعيله خلال 24 ساعة.''',
            'category': 'ads',
            'keywords': 'إعلان, نشر, مبوب, classified, ads, إنشاء',
            'priority': 9
        },
        
        # Account Registration
        {
            'question': 'كيف أنشئ حساب جديد؟',
            'answer': '''لإنشاء حساب جديد في إدريسي مارت:

1️⃣ اضغط على "تسجيل جديد"
2️⃣ أدخل بياناتك (الاسم، البريد الإلكتروني، كلمة المرور)
3️⃣ اختر نوع الحساب (فردي، تاجر، مؤسسة تعليمية، إلخ)
4️⃣ وافق على الشروط والأحكام
5️⃣ اضغط "إنشاء الحساب"
6️⃣ تحقق من بريدك الإلكتروني لتفعيل الحساب

بعد التفعيل يمكنك الاستفادة من جميع خدمات المنصة.''',
            'category': 'account',
            'keywords': 'حساب, تسجيل, إنشاء, register, account, signup',
            'priority': 9
        },
        
        # Payment Methods
        {
            'question': 'ما هي طرق الدفع المتاحة؟',
            'answer': '''نوفر طرق دفع متنوعة وآمنة:

💳 PayPal - للدفع الدولي الآمن
💳 Paymob - للدفع المحلي في مصر والسعودية  
💳 التحويل البنكي - للمبالغ الكبيرة
💳 الدفع عند الاستلام - للطلبات المحلية

جميع المعاملات محمية بأعلى معايير الأمان والتشفير.
نحن لا نحتفظ ببيانات بطاقاتك الائتمانية لضمان أمانك.''',
            'category': 'payment',
            'keywords': 'دفع, payment, paypal, paymob, بطاقة, تحويل',
            'priority': 8
        },
        
        # Mobile Verification
        {
            'question': 'لماذا أحتاج للتحقق من رقم الجوال؟',
            'answer': '''التحقق من رقم الجوال مطلوب لضمان:

🔒 أمان حسابك وحماية من الاحتيال
📱 التواصل السريع مع المشترين والبائعين
✅ تأكيد هويتك كمستخدم حقيقي
🚫 منع الحسابات الوهمية والمزيفة
📞 إرسال تنبيهات مهمة عبر SMS

عملية التحقق سريعة وآمنة عبر رمز OTP يصلك خلال دقائق.''',
            'category': 'account',
            'keywords': 'تحقق, جوال, موبايل, otp, رقم, verification, mobile',
            'priority': 7
        },
        
        # Marketplace
        {
            'question': 'كيف أبيع منتجاتي في المتجر؟',
            'answer': '''للبيع في متجر إدريسي مارت:

1️⃣ أنشئ حساب تاجر
2️⃣ اختر باقة التاجر المناسبة
3️⃣ أضف معلومات متجرك
4️⃣ ارفع منتجاتك مع الصور والأوصاف
5️⃣ حدد أسعار وطرق الشحن
6️⃣ فعل خيارات الدفع
7️⃣ ابدأ البيع واستقبال الطلبات

نوفر لك لوحة تحكم شاملة لإدارة متجرك ومتابعة المبيعات.''',
            'category': 'marketplace',
            'keywords': 'متجر, بيع, منتجات, تاجر, marketplace, store, sell',
            'priority': 8
        },
        
        # Support
        {
            'question': 'كيف أتواصل مع الدعم الفني؟',
            'answer': '''يمكنك التواصل مع فريق الدعم الفني عبر:

📧 البريد الإلكتروني: support@idrissimart.com
📱 الواتساب: +20 11 27078236
🕒 ساعات العمل: الأحد - الخميس من 9 صباحاً - 5 مساءً
💬 الدردشة المباشرة: متاحة على الموقع
📝 نموذج التواصل: في صفحة "اتصل بنا"

فريقنا مستعد لمساعدتك في أي وقت!''',
            'category': 'support',
            'keywords': 'دعم, مساعدة, تواصل, support, help, contact',
            'priority': 9
        },
        
        # Values - Comprehensive
        {
            'question': 'ما هي قيم إدريسي مارت؟',
            'answer': '''قيمنا المؤسسية الأساسية:

🌟 الشمولية - نقدم جميع خدمات السوق في منصة واحدة متكاملة
⚙️ التكنولوجيا الحديثة - نستخدم أحدث التقنيات الرقمية
🔒 الثقة والأمان - أعلى مستويات الأمان وحماية البيانات
🎯 الجودة والتميز - نسعى للتميز في كل ما نقدمه

هذه القيم توجه كل قراراتنا وخدماتنا لضمان أفضل تجربة للمستخدمين.''',
            'category': 'about',
            'keywords': 'قيم, values, مبادئ, أساس, فلسفة',
            'priority': 6
        }
    ]
    
    # Create knowledge base entries
    for data in knowledge_data:
        ChatbotKnowledgeBase.objects.get_or_create(
            question=data['question'],
            defaults=data
        )
    
    # Create quick actions
    quick_actions_data = [
        {
            'title': 'ما هو إدريسي مارت؟',
            'action_type': 'message',
            'action_value': 'ما هو إدريسي مارت؟',
            'icon': 'fas fa-info-circle',
            'order': 1
        },
        {
            'title': 'كيف أنشر إعلان؟',
            'action_type': 'message', 
            'action_value': 'كيف أنشر إعلان مبوب؟',
            'icon': 'fas fa-plus-circle',
            'order': 2
        },
        {
            'title': 'طرق الدفع',
            'action_type': 'message',
            'action_value': 'ما هي طرق الدفع المتاحة؟',
            'icon': 'fas fa-credit-card',
            'order': 3
        },
        {
            'title': 'إنشاء حساب',
            'action_type': 'message',
            'action_value': 'كيف أنشئ حساب جديد؟',
            'icon': 'fas fa-user-plus',
            'order': 4
        },
        {
            'title': 'الدعم الفني',
            'action_type': 'message',
            'action_value': 'كيف أتواصل مع الدعم الفني؟',
            'icon': 'fas fa-headset',
            'order': 5
        }
    ]
    
    for action_data in quick_actions_data:
        ChatbotQuickAction.objects.get_or_create(
            title=action_data['title'],
            defaults=action_data
        )
