"""
Management command to seed initial content for site configuration models
Populates HomePage, AboutPage, ContactPage, TermsPage, and PrivacyPage with default content
"""

from django.core.management.base import BaseCommand
from content.site_config import (
    HomePage,
    AboutPage,
    ContactPage,
    TermsPage,
    PrivacyPage,
    SiteConfiguration,
)


class Command(BaseCommand):
    help = "Seed initial content for site configuration singleton models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset all fields to default values (overwrite existing data)",
        )

    def handle(self, *args, **options):
        reset = options.get("reset", False)

        self.stdout.write(self.style.WARNING("Starting site content seeding..."))

        # Seed HomePage
        self.seed_homepage(reset)

        # Seed AboutPage
        self.seed_aboutpage(reset)

        # Seed ContactPage
        self.seed_contactpage(reset)

        # Seed TermsPage
        self.seed_termspage(reset)

        # Seed PrivacyPage
        self.seed_privacypage(reset)

        # Seed SiteConfiguration
        self.seed_siteconfig(reset)

        self.stdout.write(
            self.style.SUCCESS("\n✓ All site content seeded successfully!")
        )

    def seed_homepage(self, reset=False):
        """Seed HomePage content"""
        home = HomePage.get_solo()

        if not home.hero_title or reset:
            home.hero_title = "Welcome to Idrissimart"
            home.hero_title_ar = "مرحباً بك في إدريسي مارت"

        if not home.hero_subtitle or reset:
            home.hero_subtitle = "<p>Your one-stop marketplace for all your needs</p>"
            home.hero_subtitle_ar = (
                "<p>منصة متكاملة تجمع جميع خدمات السوق في مكان واحد</p>"
            )

        if not home.hero_button_text or reset:
            home.hero_button_text = "Explore Now"
            home.hero_button_text_ar = "استكشف الآن"

        if not home.hero_button_url or reset:
            home.hero_button_url = "/ads/"

        if not home.modal_title or reset:
            home.modal_title = "Special Offer"
            home.modal_title_ar = "عرض خاص"

        if not home.modal_content or reset:
            home.modal_content = "<p>Check out our latest deals and promotions!</p>"
            home.modal_content_ar = "<p>تحقق من أحدث العروض والخصومات!</p>"

        home.show_featured_categories = True
        home.show_featured_ads = True

        home.save()
        self.stdout.write(self.style.SUCCESS("✓ HomePage seeded"))

    def seed_aboutpage(self, reset=False):
        """Seed AboutPage content"""
        about = AboutPage.get_solo()

        if not about.title or reset:
            about.title = "About Us"
            about.title_ar = "من نحن"

        if not about.content or reset:
            about.content = """
<p><strong>Idrissimart</strong> is an integrated platform that brings together all market services in one place,
specially designed to meet the needs of professionals and the general public alike.</p>
<p>We provide comprehensive solutions including classified ads, multi-vendor marketplace, service requests,
training courses, and job opportunities, making our platform the ideal place for all market needs.</p>
"""
            about.content_ar = """
<p><strong>إدريسي مارت</strong> هي منصة متكاملة تجمع جميع خدمات السوق في مكان واحد،
مصممة خصيصاً لتلبية احتياجات المتخصصين والجمهور العام على حد سواء.</p>
<p>نقدم حلولاً شاملة تشمل الإعلانات المبوبة، المتجر متعدد التجار، طلب الخدمات،
الدورات التدريبية، والفرص الوظيفية، مما يجعل منصتنا المكان المثالي لجميع احتياجات السوق.</p>
"""

        if not about.vision or reset:
            about.vision = """
<p>To be the leading platform that brings together all market services in one place,
providing an integrated experience for professionals and the general public through innovative
and reliable solutions in classified ads, e-commerce, and training services.</p>
"""
            about.vision_ar = """
<p>أن نكون المنصة الرائدة التي تجمع جميع خدمات السوق في مكان واحد، موفرة تجربة متكاملة
للمتخصصين والجمهور العام على حد سواء، من خلال تقديم حلول مبتكرة وموثوقة في الإعلانات
المبوبة والتجارة الإلكترونية والخدمات التدريبية.</p>
"""

        if not about.mission or reset:
            about.mission = """
<p>To provide an integrated platform that brings all market services together in one place,
ensuring ease of access and use for everyone, and delivering high-quality services in classified ads,
multi-vendor marketplace, service requests, training courses, and job opportunities with efficiency and effectiveness.</p>
"""
            about.mission_ar = """
<p>توفير منصة متكاملة تجمع جميع خدمات السوق في مكان واحد، مع ضمان سهولة الوصول والاستخدام
للجميع، وتقديم خدمات عالية الجودة في الإعلانات المبوبة، المتجر متعدد التجار، طلب الخدمات،
الدورات التدريبية، والفرص الوظيفية بكفاءة وفعالية.</p>
"""

        if not about.values or reset:
            about.values = """
<div class="values-grid">
    <div class="value-card">
        <h3>Comprehensiveness</h3>
        <p>We provide all market services in one integrated and easy-to-use platform</p>
    </div>
    <div class="value-card">
        <h3>Modern Technology</h3>
        <p>We use the latest digital technologies to ensure an outstanding and secure user experience</p>
    </div>
    <div class="value-card">
        <h3>Trust & Security</h3>
        <p>We guarantee secure transactions and protect user data with the highest standards</p>
    </div>
    <div class="value-card">
        <h3>Quality</h3>
        <p>We are committed to providing high-quality services that meet customer expectations</p>
    </div>
    <div class="value-card">
        <h3>Innovation</h3>
        <p>We continuously develop our services to keep pace with market changes and user needs</p>
    </div>
    <div class="value-card">
        <h3>Accessibility</h3>
        <p>Platform available to everyone anytime, anywhere with an easy-to-use interface</p>
    </div>
</div>
"""
            about.values_ar = """
<div class="values-grid">
    <div class="value-card">
        <h3>الشمولية</h3>
        <p>نقدم جميع خدمات السوق في منصة واحدة متكاملة وسهلة الاستخدام</p>
    </div>
    <div class="value-card">
        <h3>التكنولوجيا الحديثة</h3>
        <p>نستخدم أحدث التقنيات الرقمية لضمان تجربة مستخدم متميزة وآمنة</p>
    </div>
    <div class="value-card">
        <h3>الثقة والأمان</h3>
        <p>نضمن معاملات آمنة وحماية بيانات المستخدمين بأعلى المعايير</p>
    </div>
    <div class="value-card">
        <h3>الجودة</h3>
        <p>نلتزم بتقديم خدمات عالية الجودة تلبي توقعات العملاء</p>
    </div>
    <div class="value-card">
        <h3>الابتكار</h3>
        <p>نطور خدماتنا باستمرار لمواكبة تغيرات السوق واحتياجات المستخدمين</p>
    </div>
    <div class="value-card">
        <h3>سهولة الوصول</h3>
        <p>منصة متاحة للجميع في أي وقت ومن أي مكان مع واجهة سهلة الاستخدام</p>
    </div>
</div>
"""

        about.save()
        self.stdout.write(self.style.SUCCESS("✓ AboutPage seeded"))

    def seed_contactpage(self, reset=False):
        """Seed ContactPage content"""
        contact = ContactPage.get_solo()

        if not contact.title or reset:
            contact.title = "Contact Us"
            contact.title_ar = "اتصل بنا"

        if not contact.description or reset:
            contact.description = """
<p>Get in touch with the Idrissimart team for support and assistance on your digital journey</p>
"""
            contact.description_ar = """
<p>تواصل مع فريق منصة إدريسي مارت للحصول على المساعدة والدعم في رحلتك الرقمية</p>
"""

        if not contact.office_hours or reset:
            contact.office_hours = """
<p>Saturday - Thursday: 8:00 AM - 6:00 PM<br>
Friday: Closed</p>
"""
            contact.office_hours_ar = """
<p>السبت - الخميس: 8:00 ص - 6:00 م<br>
الجمعة: مغلق</p>
"""

        if not contact.map_embed_code or reset:
            contact.map_embed_code = """
<iframe src="https://www.google.com/maps/embed?pb=!1m17!1m12!1m3!1d3453.2516743776344!2d31.524689175467885!3d30.023110574891097!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m2!1m1!2zMzDCsDAxJzIzLjIiTiAzMcKwMzEnMzguOSJF!5e0!3m2!1sen!2seg!4v1729244880000!5m2!1sen!2seg"
        width="100%"
        height="450"
        style="border: 0"
        allowfullscreen
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
        title="Our Location">
</iframe>
"""
            contact.map_embed_code_ar = contact.map_embed_code

        contact.enable_contact_form = True

        contact.save()
        self.stdout.write(self.style.SUCCESS("✓ ContactPage seeded"))

    def seed_termspage(self, reset=False):
        """Seed TermsPage content"""
        terms = TermsPage.get_solo()

        if not terms.title or reset:
            terms.title = "Terms and Conditions"
            terms.title_ar = "الشروط والأحكام"

        if not terms.content or reset:
            terms.content = """
<div class="policy-block">
    <h2 class="policy-title">Introduction</h2>
    <p class="policy-text">
        Welcome to Idrissimart. By accessing and using this website, you agree to comply with these terms and conditions.
        If you do not agree with any part of these terms, you should not use our website.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Account Terms</h2>
    <ul class="policy-list">
        <li>You must be 18 years or older to use this service</li>
        <li>You must provide accurate and complete information when creating an account</li>
        <li>You are responsible for maintaining the confidentiality of your password</li>
        <li>You are responsible for all activities that occur under your account</li>
        <li>You must notify us immediately of any unauthorized use of your account</li>
        <li>We reserve the right to suspend or terminate your account at any time for any reason</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">User Obligations</h2>
    <p class="policy-text">When using our platform, you agree to:</p>
    <ul class="policy-list">
        <li>Comply with all applicable laws and regulations</li>
        <li>Not post false, misleading, or fraudulent content</li>
        <li>Not violate any intellectual property rights</li>
        <li>Not use the platform for illegal activities</li>
        <li>Respect other users and maintain professional conduct</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">Prohibited Activities</h2>
    <p class="policy-text">You may not:</p>
    <ul class="policy-list">
        <li>Post spam or unsolicited advertisements</li>
        <li>Attempt to gain unauthorized access to our systems</li>
        <li>Use automated tools to access the platform without permission</li>
        <li>Harass, abuse, or harm other users</li>
        <li>Post offensive, defamatory, or inappropriate content</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">Payment Terms</h2>
    <p class="policy-text">
        All payments must be made through our approved payment methods. We reserve the right to modify pricing at any time.
        Refunds are subject to our refund policy.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Intellectual Property</h2>
    <p class="policy-text">
        All content on this platform, including text, graphics, logos, and software, is the property of Idrissimart
        or its content suppliers and is protected by copyright and other intellectual property laws.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Limitation of Liability</h2>
    <p class="policy-text">
        Idrissimart shall not be liable for any indirect, incidental, special, or consequential damages arising from
        your use of the platform. Our total liability shall not exceed the amount you paid for our services.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Changes to Terms</h2>
    <p class="policy-text">
        We reserve the right to modify these terms at any time. Continued use of the platform after changes
        constitutes acceptance of the modified terms.
    </p>
</div>
"""
            terms.content_ar = """
<div class="policy-block">
    <h2 class="policy-title">المقدمة</h2>
    <p class="policy-text">
        مرحباً بك في إدريسي مارت. من خلال الوصول إلى هذا الموقع واستخدامه، فإنك توافق على الالتزام بهذه
        الشروط والأحكام. إذا كنت لا توافق على أي جزء من هذه الشروط، فيجب عليك عدم استخدام موقعنا.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">شروط الحساب</h2>
    <ul class="policy-list">
        <li>يجب أن يكون عمرك 18 عامًا أو أكثر لاستخدام هذه الخدمة</li>
        <li>يجب عليك تقديم معلومات دقيقة وكاملة عند إنشاء حساب</li>
        <li>أنت مسؤول عن الحفاظ على سرية كلمة المرور الخاصة بك</li>
        <li>أنت مسؤول عن جميع الأنشطة التي تحدث تحت حسابك</li>
        <li>يجب عليك إخطارنا فورًا بأي استخدام غير مصرح به لحسابك</li>
        <li>نحتفظ بالحق في تعليق أو إنهاء حسابك في أي وقت لأي سبب</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">التزامات المستخدم</h2>
    <p class="policy-text">عند استخدام منصتنا، فإنك توافق على:</p>
    <ul class="policy-list">
        <li>الامتثال لجميع القوانين واللوائح المعمول بها</li>
        <li>عدم نشر محتوى كاذب أو مضلل أو احتيالي</li>
        <li>عدم انتهاك أي حقوق ملكية فكرية</li>
        <li>عدم استخدام المنصة لأنشطة غير قانونية</li>
        <li>احترام المستخدمين الآخرين والحفاظ على سلوك مهني</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">الأنشطة المحظورة</h2>
    <p class="policy-text">لا يجوز لك:</p>
    <ul class="policy-list">
        <li>نشر رسائل غير مرغوب فيها أو إعلانات غير مرغوب فيها</li>
        <li>محاولة الوصول غير المصرح به إلى أنظمتنا</li>
        <li>استخدام أدوات آلية للوصول إلى المنصة دون إذن</li>
        <li>مضايقة أو إساءة معاملة أو إلحاق الضرر بالمستخدمين الآخرين</li>
        <li>نشر محتوى مسيء أو تشهيري أو غير لائق</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">شروط الدفع</h2>
    <p class="policy-text">
        يجب إجراء جميع المدفوعات من خلال طرق الدفع المعتمدة لدينا. نحتفظ بالحق في تعديل الأسعار في أي وقت.
        تخضع المبالغ المستردة لسياسة الاسترداد الخاصة بنا.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">الملكية الفكرية</h2>
    <p class="policy-text">
        جميع المحتويات الموجودة على هذه المنصة، بما في ذلك النصوص والرسومات والشعارات والبرامج، هي ملك لإدريسي
        مارت أو موفري المحتوى الخاص بها ومحمية بموجب حقوق النشر وقوانين الملكية الفكرية الأخرى.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">حدود المسؤولية</h2>
    <p class="policy-text">
        لن تكون إدريسي مارت مسؤولة عن أي أضرار غير مباشرة أو عرضية أو خاصة أو تبعية تنشأ عن استخدامك للمنصة.
        لن تتجاوز مسؤوليتنا الإجمالية المبلغ الذي دفعته مقابل خدماتنا.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">تغييرات على الشروط</h2>
    <p class="policy-text">
        نحتفظ بالحق في تعديل هذه الشروط في أي وقت. يشكل الاستخدام المستمر للمنصة بعد التغييرات قبولاً للشروط المعدلة.
    </p>
</div>
"""

        terms.save()
        self.stdout.write(self.style.SUCCESS("✓ TermsPage seeded"))

    def seed_privacypage(self, reset=False):
        """Seed PrivacyPage content"""
        privacy = PrivacyPage.get_solo()

        if not privacy.title or reset:
            privacy.title = "Privacy Policy"
            privacy.title_ar = "سياسة الخصوصية"

        if not privacy.content or reset:
            privacy.content = """
<div class="policy-block">
    <h2 class="policy-title">Introduction</h2>
    <p class="policy-text">
        At Idrissimart, we are committed to protecting your privacy and the security of your personal information.
        This Privacy Policy explains how we collect, use, protect, and share information we gather about you when
        you use our website and platform.
    </p>
    <p class="policy-text">
        By using our services, you consent to the collection and use of information in accordance with this policy.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Information We Collect</h2>

    <h3 class="policy-subtitle">Personal Information</h3>
    <p class="policy-text">We may ask you to provide certain personal information that can be used to contact or identify you, including:</p>
    <ul class="policy-list">
        <li>Full name</li>
        <li>Email address</li>
        <li>Phone number</li>
        <li>Postal address</li>
        <li>Payment information (encrypted and protected)</li>
    </ul>

    <h3 class="policy-subtitle">Usage Data</h3>
    <p class="policy-text">We automatically collect certain information when you visit our platform:</p>
    <ul class="policy-list">
        <li>IP address</li>
        <li>Browser type and version</li>
        <li>Pages visited and time spent</li>
        <li>Device information</li>
        <li>Cookies and similar technologies</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">How We Use Your Information</h2>
    <p class="policy-text">We use the collected information for various purposes:</p>
    <ul class="policy-list">
        <li>To provide and maintain our services</li>
        <li>To notify you about changes to our services</li>
        <li>To provide customer support</li>
        <li>To gather analysis or valuable information to improve our services</li>
        <li>To detect, prevent and address technical issues</li>
        <li>To send promotional communications (with your consent)</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">Data Security</h2>
    <p class="policy-text">
        We implement appropriate security measures to protect your personal information from unauthorized access,
        alteration, disclosure, or destruction. This includes:
    </p>
    <ul class="policy-list">
        <li>Encryption of sensitive data</li>
        <li>Secure server infrastructure</li>
        <li>Regular security audits</li>
        <li>Access controls and authentication</li>
        <li>Employee training on data protection</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">Sharing Your Information</h2>
    <p class="policy-text">We may share your information with:</p>
    <ul class="policy-list">
        <li>Service providers who assist in our operations</li>
        <li>Payment processors (with encrypted data)</li>
        <li>Legal authorities when required by law</li>
        <li>Business partners (with your consent)</li>
    </ul>
    <p class="policy-text">We do not sell your personal information to third parties.</p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Your Rights</h2>
    <p class="policy-text">You have the right to:</p>
    <ul class="policy-list">
        <li>Access your personal data</li>
        <li>Request correction of inaccurate data</li>
        <li>Request deletion of your data</li>
        <li>Object to processing of your data</li>
        <li>Request transfer of your data</li>
        <li>Withdraw consent at any time</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">Cookies</h2>
    <p class="policy-text">
        We use cookies and similar tracking technologies to track activity on our platform and hold certain information.
        You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">Changes to This Policy</h2>
    <p class="policy-text">
        We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new
        Privacy Policy on this page and updating the "Last Updated" date.
    </p>
</div>
"""
            privacy.content_ar = """
<div class="policy-block">
    <h2 class="policy-title">المقدمة</h2>
    <p class="policy-text">
        نحن في إدريسي مارت نلتزم بحماية خصوصيتك وأمان معلوماتك الشخصية. توضح سياسة الخصوصية هذه كيفية
        جمعنا واستخدامنا وحمايتنا ومشاركتنا للمعلومات التي نجمعها عنك عند استخدام موقعنا ومنصتنا.
    </p>
    <p class="policy-text">
        باستخدامك لخدماتنا، فإنك توافق على جمع واستخدام المعلومات وفقاً لهذه السياسة.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">المعلومات التي نجمعها</h2>

    <h3 class="policy-subtitle">المعلومات الشخصية</h3>
    <p class="policy-text">قد نطلب منك تقديم معلومات شخصية معينة يمكن استخدامها للتواصل معك أو تحديد هويتك، بما في ذلك:</p>
    <ul class="policy-list">
        <li>الاسم الكامل</li>
        <li>عنوان البريد الإلكتروني</li>
        <li>رقم الهاتف</li>
        <li>العنوان البريدي</li>
        <li>معلومات الدفع (يتم تشفيرها وحمايتها)</li>
    </ul>

    <h3 class="policy-subtitle">بيانات الاستخدام</h3>
    <p class="policy-text">نقوم تلقائياً بجمع معلومات معينة عند زيارتك لمنصتنا:</p>
    <ul class="policy-list">
        <li>عنوان IP</li>
        <li>نوع المتصفح والإصدار</li>
        <li>الصفحات التي تمت زيارتها والوقت المستغرق</li>
        <li>معلومات الجهاز</li>
        <li>ملفات تعريف الارتباط والتقنيات المماثلة</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">كيف نستخدم معلوماتك</h2>
    <p class="policy-text">نستخدم المعلومات التي تم جمعها لأغراض مختلفة:</p>
    <ul class="policy-list">
        <li>لتوفير وصيانة خدماتنا</li>
        <li>لإخطارك بالتغييرات التي تطرأ على خدماتنا</li>
        <li>لتقديم دعم العملاء</li>
        <li>لجمع التحليلات أو المعلومات القيمة لتحسين خدماتنا</li>
        <li>للكشف عن المشاكل التقنية ومنعها ومعالجتها</li>
        <li>لإرسال اتصالات ترويجية (بموافقتك)</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">أمن البيانات</h2>
    <p class="policy-text">
        نطبق تدابير أمنية مناسبة لحماية معلوماتك الشخصية من الوصول غير المصرح به أو التغيير أو الكشف أو التدمير.
        يتضمن ذلك:
    </p>
    <ul class="policy-list">
        <li>تشفير البيانات الحساسة</li>
        <li>بنية تحتية آمنة للخادم</li>
        <li>عمليات تدقيق أمنية منتظمة</li>
        <li>ضوابط الوصول والمصادقة</li>
        <li>تدريب الموظفين على حماية البيانات</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">مشاركة معلوماتك</h2>
    <p class="policy-text">قد نشارك معلوماتك مع:</p>
    <ul class="policy-list">
        <li>مزودي الخدمات الذين يساعدون في عملياتنا</li>
        <li>معالجات الدفع (مع البيانات المشفرة)</li>
        <li>السلطات القانونية عندما يقتضي القانون ذلك</li>
        <li>شركاء الأعمال (بموافقتك)</li>
    </ul>
    <p class="policy-text">نحن لا نبيع معلوماتك الشخصية لأطراف ثالثة.</p>
</div>

<div class="policy-block">
    <h2 class="policy-title">حقوقك</h2>
    <p class="policy-text">لديك الحق في:</p>
    <ul class="policy-list">
        <li>الوصول إلى بياناتك الشخصية</li>
        <li>طلب تصحيح البيانات غير الدقيقة</li>
        <li>طلب حذف بياناتك</li>
        <li>الاعتراض على معالجة بياناتك</li>
        <li>طلب نقل بياناتك</li>
        <li>سحب الموافقة في أي وقت</li>
    </ul>
</div>

<div class="policy-block">
    <h2 class="policy-title">ملفات تعريف الارتباط</h2>
    <p class="policy-text">
        نستخدم ملفات تعريف الارتباط وتقنيات التتبع المماثلة لتتبع النشاط على منصتنا والاحتفاظ بمعلومات معينة.
        يمكنك توجيه متصفحك لرفض جميع ملفات تعريف الارتباط أو للإشارة عند إرسال ملف تعريف ارتباط.
    </p>
</div>

<div class="policy-block">
    <h2 class="policy-title">التغييرات على هذه السياسة</h2>
    <p class="policy-text">
        قد نقوم بتحديث سياسة الخصوصية الخاصة بنا من وقت لآخر. سنخطرك بأي تغييرات عن طريق نشر سياسة الخصوصية
        الجديدة على هذه الصفحة وتحديث تاريخ "آخر تحديث".
    </p>
</div>
"""

        privacy.save()
        self.stdout.write(self.style.SUCCESS("✓ PrivacyPage seeded"))

    def seed_siteconfig(self, reset=False):
        """Seed SiteConfiguration content"""
        config = SiteConfiguration.get_solo()

        if not config.meta_keywords or reset:
            config.meta_keywords = "marketplace, classified ads, e-commerce, multi-vendor, online shopping, services"
            config.meta_keywords_ar = "سوق إلكتروني, إعلانات مبوبة, تجارة إلكترونية, متعدد التجار, تسوق أونلاين, خدمات"

        if not config.footer_text or reset:
            config.footer_text = (
                "<p>Idrissimart - Your comprehensive marketplace for all your needs</p>"
            )
            config.footer_text_ar = "<p>إدريسي مارت - منصتك الشاملة لجميع احتياجاتك</p>"

        if not config.copyright_text or reset:
            config.copyright_text = "© 2024 إدريسي مارت. جميع الحقوق محفوظة."

        config.save()
        self.stdout.write(self.style.SUCCESS("✓ SiteConfiguration seeded"))
