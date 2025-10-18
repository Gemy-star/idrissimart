from django.core.management.base import BaseCommand

from main.models import AboutPage, CompanyValue


class Command(BaseCommand):
    help = "Populate about page content and company values"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting about page population..."))

        # Delete existing content to avoid duplicates
        AboutPage.objects.all().delete()
        CompanyValue.objects.all().delete()

        # Create the about page content
        about_page = AboutPage.objects.create(
            title="إدريسي مارت",
            tagline="منصة تجمع سوق واحد",
            subtitle="متخصص يستفيد منه المتخصصون والجمهور العام الذي يحتاج إلى أي من خدمات هذا السوق",
            who_we_are_title="من نحن؟",
            who_we_are_content="إدريسي مارت هي منصة متكاملة تجمع جميع خدمات السوق في مكان واحد، مصممة خصيصاً لتلبية احتياجات المتخصصين والجمهور العام على حد سواء. نقدم حلولاً شاملة تشمل الإعلانات المبوبة، المتجر متعدد التجار، طلب الخدمات، الدورات التدريبية، والفرص الوظيفية، مما يجعل منصتنا المكان المثالي لجميع احتياجات السوق. نسعى لخلق تجربة مستخدم فريدة تجمع بين السهولة والكفاءة، مع ضمان أعلى مستويات الجودة والموثوقية في جميع خدماتنا.",
            vision_title="رؤيتنا",
            vision_content="أن نكون المنصة الرائدة التي تجمع جميع خدمات السوق في مكان واحد، موفرة تجربة متكاملة للمتخصصين والجمهور العام على حد سواء، من خلال تقديم حلول مبتكرة وموثوقة في الإعلانات المبوبة والتجارة الإلكترونية والخدمات التدريبية.",
            mission_title="رسالتنا",
            mission_content="توفير منصة متكاملة تجمع جميع خدمات السوق في مكان واحد، مع ضمان سهولة الوصول والاستخدام للجميع، وتقديم خدمات عالية الجودة في الإعلانات المبوبة، المتجر متعدد التجار، طلب الخدمات، الدورات التدريبية، والفرص الوظيفية بكفاءة وفعالية.",
            values_title="قيمنا",
            products_count=5000,
            customers_count=25000,
            vendors_count=1200,
            categories_count=5,
            is_active=True,
        )

        # Create company values
        values_data = [
            {
                "title": "الشمولية",
                "description": "نقدم جميع خدمات السوق في منصة واحدة متكاملة وسهلة الاستخدام",
                "icon_class": "fas fa-globe",
                "order": 1,
            },
            {
                "title": "التكنولوجيا الحديثة",
                "description": "نستخدم أحدث التقنيات الرقمية لضمان تجربة مستخدم متميزة وآمنة",
                "icon_class": "fas fa-mobile-alt",
                "order": 2,
            },
            {
                "title": "الثقة والأمان",
                "description": "نضمن أعلى مستويات الأمان والخصوصية لحماية بيانات مستخدمينا",
                "icon_class": "fas fa-shield-alt",
                "order": 3,
            },
            {
                "title": "الوصول السهل",
                "description": "منصة متاحة للجميع في أي وقت ومن أي مكان مع واجهة سهلة الاستخدام",
                "icon_class": "fas fa-users",
                "order": 4,
            },
            {
                "title": "الجودة العالية",
                "description": "نلتزم بأعلى معايير الجودة في جميع خدماتنا ومنتجاتنا",
                "icon_class": "fas fa-star",
                "order": 5,
            },
            {
                "title": "الابتكار المستمر",
                "description": "نطور خدماتنا باستمرار لتلبية احتياجات مستخدمينا المتغيرة",
                "icon_class": "fas fa-lightbulb",
                "order": 6,
            },
        ]

        for value_data in values_data:
            CompanyValue.objects.create(about_page=about_page, **value_data)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ About page content created successfully!\n"
                f"   Title: {about_page.title}\n"
                f"   Tagline: {about_page.tagline}\n"
                f"   Products: {about_page.products_count}\n"
                f"   Customers: {about_page.customers_count}\n"
                f"   Vendors: {about_page.vendors_count}\n"
                f"   Company Values: {len(values_data)} values created"
            )
        )
