# Data migration to populate default AboutPageSection entries
from django.db import migrations


def create_default_sections(apps, schema_editor):
    """Create default 'Individuals' and 'Businesses' sections with content"""
    AboutPage = apps.get_model('content', 'AboutPage')
    AboutPageSection = apps.get_model('content', 'AboutPageSection')

    # Get or create the AboutPage instance (singleton)
    try:
        about_page = AboutPage.objects.get()
    except AboutPage.DoesNotExist:
        about_page = AboutPage.objects.create()

    # Create Individuals Section (Arabic)
    individuals_content_ar = """
    <div class="offerings-list">
        <div class="offering-item">
            <div class="offering-icon">📢</div>
            <p>إعلانات مبوبة متنوعة لجميع الاحتياجات اليومية</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🛒</div>
            <p>تسوق سهل وآمن من متاجر متعددة التجار</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🔧</div>
            <p>طلب خدمات متخصصة من الخبراء المعتمدين</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🎓</div>
            <p>دورات تدريبية معتمدة لتطوير المهارات المهنية</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">💼</div>
            <p>فرص وظيفية متنوعة في مختلف المجالات</p>
        </div>
    </div>
    """

    individuals_content_en = """
    <div class="offerings-list">
        <div class="offering-item">
            <div class="offering-icon">📢</div>
            <p>Diverse classified ads for all daily needs</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🛒</div>
            <p>Safe and easy shopping from multi-vendor stores</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🔧</div>
            <p>Request specialized services from certified experts</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🎓</div>
            <p>Certified training courses for professional skills development</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">💼</div>
            <p>Diverse job opportunities in various fields</p>
        </div>
    </div>
    """

    # Create Businesses Section (Arabic)
    businesses_content_ar = """
    <div class="offerings-list">
        <div class="offering-item">
            <div class="offering-icon">🏪</div>
            <p>إدارة متجر إلكتروني متكامل مع أدوات البيع المتقدمة</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">📊</div>
            <p>تحليلات شاملة لأداء المتجر وزيادة المبيعات</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🤝</div>
            <p>خدمات التواصل مع العملاء وإدارة الطلبات</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">📈</div>
            <p>أدوات التسويق والترويج للمنتجات والخدمات</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🔒</div>
            <p>أنظمة دفع آمنة وحماية كاملة للبيانات</p>
        </div>
    </div>
    """

    businesses_content_en = """
    <div class="offerings-list">
        <div class="offering-item">
            <div class="offering-icon">🏪</div>
            <p>Manage a complete online store with advanced sales tools</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">📊</div>
            <p>Comprehensive analytics for store performance and sales growth</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🤝</div>
            <p>Customer communication services and order management</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">📈</div>
            <p>Marketing and promotion tools for products and services</p>
        </div>
        <div class="offering-item">
            <div class="offering-icon">🔒</div>
            <p>Secure payment systems and complete data protection</p>
        </div>
    </div>
    """

    # Create the sections
    AboutPageSection.objects.create(
        about_page=about_page,
        tab_title="For Individuals",
        tab_title_ar="للأفراد",
        icon="👤",
        content=individuals_content_en,
        content_ar=individuals_content_ar,
        order=1,
        is_active=True
    )

    AboutPageSection.objects.create(
        about_page=about_page,
        tab_title="For Businesses",
        tab_title_ar="للشركات والتجار",
        icon="🏢",
        content=businesses_content_en,
        content_ar=businesses_content_ar,
        order=2,
        is_active=True
    )


def reverse_migration(apps, schema_editor):
    """Remove the default sections"""
    AboutPageSection = apps.get_model('content', 'AboutPageSection')
    AboutPageSection.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_add_about_page_sections'),
    ]

    operations = [
        migrations.RunPython(create_default_sections, reverse_migration),
    ]
