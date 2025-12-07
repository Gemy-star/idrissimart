# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from main.models import FAQCategory, FAQ


class Command(BaseCommand):
    help = "Populate FAQ with default questions and answers"

    def handle(self, *args, **options):
        self.stdout.write("Populating FAQ...")

        # Delete all existing FAQs and categories
        deleted_faqs = FAQ.objects.all().delete()
        deleted_categories = FAQCategory.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(
                f"Deleted {deleted_faqs[0]} FAQs and {deleted_categories[0]} categories"
            )
        )

        # Create categories
        categories_data = [
            {
                "name": "General Questions",
                "name_ar": "أسئلة عامة",
                "icon": "fas fa-question-circle",
                "order": 1,
            },
            {
                "name": "Ads",
                "name_ar": "الإعلانات",
                "icon": "fas fa-bullhorn",
                "order": 2,
            },
            {
                "name": "Safety & Security",
                "name_ar": "الأمان والخصوصية",
                "icon": "fas fa-shield-alt",
                "order": 3,
            },
            {
                "name": "Payment & Packages",
                "name_ar": "الدفع والباقات",
                "icon": "fas fa-credit-card",
                "order": 4,
            },
            {
                "name": "Technical Support",
                "name_ar": "الدعم الفني",
                "icon": "fas fa-headset",
                "order": 5,
            },
        ]

        created_categories = 0
        for cat_data in categories_data:
            category, created = FAQCategory.objects.update_or_create(
                name=cat_data["name"], defaults=cat_data
            )
            if created:
                created_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created category: {category.name}")
                )

        # Create FAQs
        faqs_data = [
            # General Questions
            {
                "category": "General Questions",
                "question": "What is Idrisi Mart?",
                "question_ar": "ما هو إدريسي مارت؟",
                "answer": "Idrisi Mart is a comprehensive platform that brings together all services and products in one place to facilitate the search process and access to what you need. We provide a safe and reliable platform for classified ads in various fields.",
                "answer_ar": "إدريسي مارت هي منصة شاملة تجمع كافة الخدمات والمنتجات في مكان واحد لتسهيل عملية البحث والوصول إلى ما تحتاجه. نوفر منصة آمنة وموثوقة للإعلانات المبوبة في مختلف المجالات.",
                "order": 1,
                "is_popular": True,
            },
            {
                "category": "General Questions",
                "question": "How do I create an account?",
                "question_ar": "كيف أقوم بإنشاء حساب؟",
                "answer": "To register on the site, click the 'Register' button at the top of the page, then fill in the required information such as name, email, and password. After that, activate your account via the email sent to you.",
                "answer_ar": "للتسجيل في الموقع، انقر على زر 'تسجيل' في أعلى الصفحة، ثم قم بملء البيانات المطلوبة مثل الاسم والبريد الإلكتروني وكلمة المرور. بعد ذلك قم بتفعيل حسابك عبر البريد الإلكتروني المرسل إليك.",
                "order": 2,
            },
            {
                "category": "General Questions",
                "question": "Is registration free?",
                "question_ar": "هل التسجيل مجاني؟",
                "answer": "Yes, registration on the site is completely free. You can create an account and start using the platform at no cost. There are optional premium services for those who wish to upgrade their ads.",
                "answer_ar": "نعم، التسجيل في الموقع مجاني تماماً. يمكنك إنشاء حساب والبدء في استخدام المنصة بدون أي تكاليف. هناك خدمات مميزة مدفوعة اختيارية لمن يرغب في ترقية إعلاناته.",
                "order": 3,
            },
            # Ads
            {
                "category": "Ads",
                "question": "How do I post an ad?",
                "question_ar": "كيف أقوم بنشر إعلان؟",
                "answer": "After logging in, click the 'Post Ad' button at the top of the page. Choose the appropriate category, fill in the ad details, add images, then click 'Post Ad'. Your ad will be reviewed by our team before publication.",
                "answer_ar": "بعد تسجيل الدخول، انقر على زر 'نشر إعلان' في أعلى الصفحة. اختر القسم المناسب، املأ تفاصيل الإعلان، أضف الصور، ثم انقر على 'نشر الإعلان'. سيتم مراجعة إعلانك من قبل فريقنا قبل نشره.",
                "order": 1,
                "is_popular": True,
            },
            {
                "category": "Ads",
                "question": "How many images can I add to an ad?",
                "question_ar": "كم عدد الصور التي يمكنني إضافتها للإعلان؟",
                "answer": "You can add up to 10 images per ad. We recommend adding clear and high-quality images to increase the success rate of your ad.",
                "answer_ar": "يمكنك إضافة حتى 10 صور لكل إعلان. ننصح بإضافة صور واضحة وعالية الجودة لزيادة فرص نجاح إعلانك.",
                "order": 2,
            },
            {
                "category": "Ads",
                "question": "How long does it take to publish an ad?",
                "question_ar": "كم من الوقت يستغرق نشر الإعلان؟",
                "answer": "Ads are usually reviewed and published within 24 hours of submission. In the case of featured or urgent ads, publication is faster.",
                "answer_ar": "عادة يتم مراجعة ونشر الإعلانات خلال 24 ساعة من تقديمها. في حالة الإعلانات المميزة أو العاجلة، يتم النشر بشكل أسرع.",
                "order": 3,
            },
            {
                "category": "Ads",
                "question": "How can I edit or delete my ad?",
                "question_ar": "كيف يمكنني تعديل أو حذف إعلاني؟",
                "answer": "You can edit or delete your ad from your control panel. Click on 'My Ads', then select the ad you want to edit or delete and press the appropriate button.",
                "answer_ar": "يمكنك تعديل أو حذف إعلانك من خلال لوحة التحكم الخاصة بك. انقر على 'إعلاناتي' ثم اختر الإعلان المراد تعديله أو حذفه واضغط على الزر المناسب.",
                "order": 4,
            },
            # Safety
            {
                "category": "Safety & Security",
                "question": "How do you protect my personal data?",
                "question_ar": "كيف تحمون بياناتي الشخصية؟",
                "answer": "We use the latest encryption technologies and security protocols to protect your personal data. All sensitive information is encrypted and never shared with any third parties. You can review our privacy policy for more details.",
                "answer_ar": "نحن نستخدم أحدث تقنيات التشفير وبروتوكولات الأمان لحماية بياناتك الشخصية. جميع المعلومات الحساسة يتم تشفيرها ولا يتم مشاركتها مع أي جهة خارجية. يمكنك مراجعة سياسة الخصوصية للمزيد من التفاصيل.",
                "order": 1,
                "is_popular": True,
            },
            {
                "category": "Safety & Security",
                "question": "How do I report a suspicious ad?",
                "question_ar": "كيف أبلغ عن إعلان مشبوه؟",
                "answer": "If you find a suspicious or violating ad, you can click the 'Report' button on the ad page. The report will be reviewed by our team and appropriate action will be taken.",
                "answer_ar": "إذا وجدت إعلاناً مشبوهاً أو مخالفاً، يمكنك الضغط على زر 'إبلاغ' الموجود في صفحة الإعلان. سيتم مراجعة البلاغ من قبل فريقنا واتخاذ الإجراءات المناسبة.",
                "order": 2,
            },
            {
                "category": "Safety & Security",
                "question": "Can I hide my phone number?",
                "question_ar": "هل يمكنني إخفاء رقم هاتفي؟",
                "answer": "Yes, you can choose to hide your phone number and receive messages through the site's internal messaging system. This helps protect your privacy.",
                "answer_ar": "نعم، يمكنك اختيار إخفاء رقم هاتفك واستقبال الرسائل عبر نظام المراسلة الداخلي في الموقع. هذا يساعد في حماية خصوصيتك.",
                "order": 3,
            },
            # Payment
            {
                "category": "Payment & Packages",
                "question": "What payment methods are available?",
                "question_ar": "ما هي طرق الدفع المتاحة؟",
                "answer": "We offer several payment methods including: credit cards (Visa/Mastercard), electronic payment, and bank transfer. All transactions are secure and encrypted.",
                "answer_ar": "نوفر عدة طرق للدفع تشمل: الدفع بالبطاقات الائتمانية (Visa/Mastercard)، الدفع الإلكتروني، والتحويل البنكي. جميع المعاملات آمنة ومشفرة.",
                "order": 1,
            },
            {
                "category": "Payment & Packages",
                "question": "What's the difference between regular and featured ads?",
                "question_ar": "ما الفرق بين الإعلان العادي والمميز؟",
                "answer": "Featured ads appear at the top of search results and on the home page, increasing their visibility. They also get a 'Featured' badge and remain visible for a longer period.",
                "answer_ar": "الإعلانات المميزة تظهر في أعلى نتائج البحث وفي الصفحة الرئيسية، مما يزيد من فرص مشاهدتها. كما تحصل على شارة 'مميز' وتبقى مرئية لفترة أطول.",
                "order": 2,
                "is_popular": True,
            },
            {
                "category": "Payment & Packages",
                "question": "Can I get a refund if I'm not satisfied?",
                "question_ar": "هل يمكنني استرداد المبلغ إذا لم أكن راضياً؟",
                "answer": "You can request a refund within 7 days of purchase if the service has not been activated yet. Please review our refund terms and conditions for more details.",
                "answer_ar": "يمكنك طلب استرداد المبلغ خلال 7 أيام من الشراء إذا لم يتم تفعيل الخدمة بعد. يرجى مراجعة شروط وأحكام الاسترداد للمزيد من التفاصيل.",
                "order": 3,
            },
            # Support
            {
                "category": "Technical Support",
                "question": "How can I contact technical support?",
                "question_ar": "كيف يمكنني التواصل مع الدعم الفني؟",
                "answer": "You can contact us through the 'Contact Us' page or via email or WhatsApp. Our support team is available Saturday to Thursday from 9 AM to 5 PM.",
                "answer_ar": "يمكنك التواصل معنا عبر صفحة 'اتصل بنا' أو من خلال البريد الإلكتروني أو الواتساب. فريق الدعم متاح من السبت إلى الخميس من 9 صباحاً حتى 5 مساءً.",
                "order": 1,
            },
            {
                "category": "Technical Support",
                "question": "What should I do if I forgot my password?",
                "question_ar": "ماذا أفعل إذا نسيت كلمة المرور؟",
                "answer": "Click 'Forgot Password?' on the login page, then enter your email address. We will send you a link to reset your password.",
                "answer_ar": "انقر على 'نسيت كلمة المرور؟' في صفحة تسجيل الدخول، ثم أدخل بريدك الإلكتروني. سنرسل لك رابطاً لإعادة تعيين كلمة المرور.",
                "order": 2,
            },
        ]

        created_faqs = 0
        for faq_data in faqs_data:
            category_name = faq_data.pop("category")
            category = FAQCategory.objects.get(name=category_name)

            faq, created = FAQ.objects.update_or_create(
                category=category,
                question=faq_data["question"],
                defaults={**faq_data, "category": category},
            )

            if created:
                created_faqs += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created FAQ: {faq.question[:50]}...")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully populated FAQ!\nCategories created: {created_categories}\nFAQs created: {created_faqs}"
            )
        )
