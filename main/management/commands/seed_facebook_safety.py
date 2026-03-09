"""
Django management command to seed Facebook Share Requests and Safety Tips data
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from main.models import (
    User, FacebookShareRequest, SafetyTip,
    ClassifiedAd, Category
)


class Command(BaseCommand):
    help = "Seed Facebook Share Requests and Safety Tips data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--facebook-requests",
            type=int,
            default=20,
            help="Number of Facebook share requests to create (default: 20)",
        )
        parser.add_argument(
            "--safety-tips",
            type=int,
            default=15,
            help="Number of safety tips to create (default: 15)",
        )
        parser.add_argument(
            "--clear-facebook",
            action="store_true",
            help="Clear existing Facebook share requests before seeding",
        )
        parser.add_argument(
            "--clear-tips",
            action="store_true",
            help="Clear existing safety tips before seeding",
        )
        parser.add_argument(
            "--clear-all",
            action="store_true",
            help="Clear all existing data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_facebook = options["facebook_requests"]
        num_tips = options["safety_tips"]
        clear_facebook = options["clear_facebook"] or options["clear_all"]
        clear_tips = options["clear_tips"] or options["clear_all"]

        self.stdout.write(self.style.WARNING("\n🌱 Starting Facebook & Safety Tips data seeding...\n"))

        # Clear existing data if requested
        if clear_facebook:
            self.stdout.write(self.style.WARNING("Clearing existing Facebook share requests..."))
            FacebookShareRequest.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared Facebook requests\n"))

        if clear_tips:
            self.stdout.write(self.style.WARNING("Clearing existing safety tips..."))
            SafetyTip.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared safety tips\n"))

        # Get existing data
        ads = list(ClassifiedAd.objects.filter(status='active')[:100])
        categories = list(Category.objects.all())
        superusers = list(User.objects.filter(is_superuser=True))

        if not ads:
            self.stdout.write(self.style.ERROR("❌ No active ads found. Please create some ads first."))
            return

        if not categories:
            self.stdout.write(self.style.ERROR("❌ No categories found. Please create categories first."))
            return

        if not superusers:
            self.stdout.write(self.style.ERROR("❌ No superusers found. Please create a superuser first."))
            return

        # Seed Facebook Share Requests
        if num_facebook > 0:
            self.stdout.write(self.style.HTTP_INFO(f"Creating {num_facebook} Facebook share requests..."))
            created_facebook = self._seed_facebook_requests(num_facebook, ads, superusers)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {created_facebook} Facebook share requests\n"))

        # Seed Safety Tips
        if num_tips > 0:
            self.stdout.write(self.style.HTTP_INFO(f"Creating {num_tips} safety tips..."))
            created_tips = self._seed_safety_tips(num_tips, categories)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {created_tips} safety tips\n"))

        self.stdout.write(self.style.SUCCESS("🎉 Seeding completed successfully!\n"))

    def _seed_facebook_requests(self, count, ads, superusers):
        """Create fake Facebook share requests"""
        statuses = ['pending', 'in_progress', 'completed', 'rejected']
        status_weights = [0.3, 0.2, 0.4, 0.1]  # More completed/pending for realism

        created = 0
        for i in range(count):
            ad = random.choice(ads)
            status = random.choices(statuses, weights=status_weights)[0]

            # Calculate request date
            days_ago = random.randint(1, 90)
            requested_at = timezone.now() - timedelta(days=days_ago)

            # Payment details
            payment_amount = Decimal(str(random.choice([50.00, 75.00, 100.00])))
            payment_confirmed = random.choice([True, False]) if status != 'pending' else False

            # Create request
            request = FacebookShareRequest.objects.create(
                ad=ad,
                user=ad.user,
                status=status,
                payment_amount=payment_amount,
                payment_confirmed=payment_confirmed,
                requested_at=requested_at,
            )

            # If processed, add processing details
            if status in ['completed', 'rejected', 'in_progress']:
                process_days = random.randint(1, 5)
                request.processed_at = requested_at + timedelta(days=process_days)
                request.processed_by = random.choice(superusers)

                if status == 'completed':
                    request.facebook_post_url = f"https://facebook.com/idrissimart/posts/{random.randint(10000, 99999)}"
                    request.admin_notes = random.choice([
                        "تم النشر بنجاح على الصفحة الرسمية",
                        "تم النشر مع إضافة وسوم مناسبة",
                        "نشر ممتاز، حصل على تفاعل جيد",
                    ])
                elif status == 'rejected':
                    request.admin_notes = random.choice([
                        "الإعلان لا يتوافق مع سياسة النشر",
                        "يرجى تحسين جودة الصورة",
                        "المحتوى يحتاج إلى مراجعة",
                    ])
                elif status == 'in_progress':
                    request.admin_notes = "جاري المراجعة والنشر قريباً"

                request.save()

            created += 1

        return created

    def _seed_safety_tips(self, count, categories):
        """Create fake safety tips"""
        color_themes = ['tip-blue', 'tip-green', 'tip-red', 'tip-yellow', 'tip-purple', 'tip-orange']
        icon_classes = [
            'fas fa-shield-alt',
            'fas fa-lock',
            'fas fa-eye',
            'fas fa-user-shield',
            'fas fa-exclamation-triangle',
            'fas fa-handshake',
            'fas fa-check-circle',
            'fas fa-info-circle',
            'fas fa-bell',
            'fas fa-map-marker-alt',
        ]

        # Safety tip templates (Arabic and English)
        tip_templates = [
            {
                'title': 'تحقق من هوية البائع',
                'title_en': 'Verify Seller Identity',
                'description': 'تأكد دائماً من هوية البائع من خلال التواصل المباشر ومراجعة تقييماته قبل إتمام أي صفقة.',
                'description_en': 'Always verify the seller\'s identity through direct communication and review their ratings before completing any deal.',
            },
            {
                'title': 'الاجتماع في أماكن عامة',
                'title_en': 'Meet in Public Places',
                'description': 'اختر دائماً أماكن عامة ومزدحمة للقاء البائع وفحص المنتج بدلاً من الأماكن الخاصة.',
                'description_en': 'Always choose public and crowded places to meet the seller and inspect the product instead of private locations.',
            },
            {
                'title': 'فحص المنتج قبل الدفع',
                'title_en': 'Inspect Before Payment',
                'description': 'افحص المنتج بعناية وتأكد من مطابقته للوصف قبل دفع أي مبالغ مالية.',
                'description_en': 'Carefully inspect the product and ensure it matches the description before making any payment.',
            },
            {
                'title': 'تجنب التحويلات المسبقة',
                'title_en': 'Avoid Advance Transfers',
                'description': 'لا تقم بتحويل أموال قبل رؤية المنتج والتأكد من جودته ومطابقته للوصف.',
                'description_en': 'Do not transfer money before seeing the product and confirming its quality and description match.',
            },
            {
                'title': 'استخدم وسائل دفع آمنة',
                'title_en': 'Use Secure Payment Methods',
                'description': 'استخدم وسائل الدفع الآمنة والموثوقة التي توفر حماية للمشتري مثل الدفع عند الاستلام.',
                'description_en': 'Use secure and trusted payment methods that provide buyer protection such as cash on delivery.',
            },
            {
                'title': 'احذر من الأسعار المنخفضة جداً',
                'title_en': 'Beware of Very Low Prices',
                'description': 'كن حذراً من الإعلانات ذات الأسعار المنخفضة بشكل غير طبيعي، فقد تكون احتيالية.',
                'description_en': 'Be cautious of ads with unusually low prices, as they may be fraudulent.',
            },
            {
                'title': 'لا تشارك معلوماتك الشخصية',
                'title_en': 'Don\'t Share Personal Info',
                'description': 'لا تشارك معلوماتك الشخصية الحساسة مثل كلمات المرور أو أرقام البطاقات البنكية.',
                'description_en': 'Do not share sensitive personal information such as passwords or bank card numbers.',
            },
            {
                'title': 'وثق الاتفاق كتابياً',
                'title_en': 'Document Agreement in Writing',
                'description': 'احتفظ بنسخة من الاتفاق والرسائل المتبادلة مع البائع كدليل في حال حدوث أي مشكلة.',
                'description_en': 'Keep a copy of the agreement and messages exchanged with the seller as evidence in case of any issues.',
            },
            {
                'title': 'اصطحب شخصاً معك',
                'title_en': 'Bring Someone With You',
                'description': 'من الأفضل اصطحاب صديق أو أحد أفراد العائلة معك عند لقاء البائع.',
                'description_en': 'It\'s better to bring a friend or family member with you when meeting the seller.',
            },
            {
                'title': 'تحقق من الضمان',
                'title_en': 'Check Warranty',
                'description': 'تأكد من وجود ضمان ساري المفعول للمنتجات الإلكترونية والأجهزة المستعملة.',
                'description_en': 'Ensure there is a valid warranty for electronic products and used devices.',
            },
            {
                'title': 'راجع الوثائق الرسمية',
                'title_en': 'Review Official Documents',
                'description': 'للسيارات والعقارات، راجع جميع الوثائق الرسمية وتأكد من صحتها قبل الشراء.',
                'description_en': 'For cars and real estate, review all official documents and verify their authenticity before purchase.',
            },
            {
                'title': 'ثق بحدسك',
                'title_en': 'Trust Your Instincts',
                'description': 'إذا شعرت بأن هناك شيئاً غير طبيعي في التعامل، لا تتردد في الانسحاب من الصفقة.',
                'description_en': 'If you feel something is unusual in the transaction, don\'t hesitate to back out of the deal.',
            },
            {
                'title': 'استخدم نظام الرسائل الداخلي',
                'title_en': 'Use Internal Messaging',
                'description': 'تواصل مع البائعين من خلال نظام الرسائل داخل المنصة للحفاظ على سجل للمحادثات.',
                'description_en': 'Communicate with sellers through the platform\'s internal messaging system to maintain a record of conversations.',
            },
            {
                'title': 'تأكد من ملكية المنتج',
                'title_en': 'Verify Product Ownership',
                'description': 'اطلب إثباتاً على أن البائع هو المالك الفعلي للمنتج وليس وسيطاً.',
                'description_en': 'Ask for proof that the seller is the actual owner of the product and not an intermediary.',
            },
            {
                'title': 'قم بالبحث عن المنتج',
                'title_en': 'Research the Product',
                'description': 'ابحث عن المنتج عبر الإنترنت لمعرفة سعره الحقيقي ومواصفاته قبل الشراء.',
                'description_en': 'Research the product online to know its real price and specifications before buying.',
            },
        ]

        created = 0
        used_templates = []

        for i in range(min(count, len(tip_templates) * 2)):  # Allow reuse with different categories
            # Select a template
            if not used_templates or (i >= len(tip_templates) and random.random() > 0.5):
                # Reuse a template with different category
                template = random.choice(tip_templates)
            else:
                # Use unused template
                available = [t for t in tip_templates if t not in used_templates]
                if not available:
                    used_templates = []
                    available = tip_templates
                template = random.choice(available)
                used_templates.append(template)

            # Randomly assign category (50% general, 50% specific category)
            category = random.choice(categories) if random.random() > 0.5 else None

            # Create safety tip
            tip = SafetyTip.objects.create(
                title=template['title'],
                title_en=template['title_en'],
                description=template['description'],
                description_en=template['description_en'],
                icon_class=random.choice(icon_classes),
                color_theme=random.choice(color_themes),
                category=category,
                is_active=random.choice([True, True, True, False]),  # 75% active
                order=i * 10,
            )

            # Add to multiple categories (30% chance)
            if random.random() > 0.7 and len(categories) > 3:
                multi_cats = random.sample(categories, random.randint(1, 3))
                tip.categories.set(multi_cats)

            created += 1

        return created
