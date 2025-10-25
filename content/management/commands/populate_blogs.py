import os
import random

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from content.models import Blog
from main.models import User


class Command(BaseCommand):
    """
    A custom management command to populate the database with dummy blog posts.

    This command is useful for testing and development, allowing you to quickly
    generate blog content. It specifically targets a category related to
    'Surveying Engineering' and assigns a default logo as the blog image.

    Example usage:
    python manage.py populate_blogs 20
    """

    help = "Populates the database with dummy blog posts."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "total",
            type=int,
            help="Indicates the number of blog posts to be created.",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        total = kwargs["total"]
        fake = Faker("ar_SA")

        self.stdout.write(
            self.style.SUCCESS(f"Starting to populate {total} blog posts...")
        )

        # --- 1. Get required objects ---
        # Get a superuser to be the author of the blogs
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            self.stderr.write(
                self.style.ERROR(
                    "No superuser found. Please create a superuser to be the blog author."
                )
            )
            return

        # --- 2. Prepare static image ---
        image_path = os.path.join(
            settings.BASE_DIR, "static", "images", "logos", "logo.png"
        )
        if not os.path.exists(image_path):
            self.stderr.write(self.style.ERROR(f"Image not found at: {image_path}"))
            return

        # --- 3. Create Blog Posts ---
        blog_content_templates = {
            "أحدث تقنيات المسح الجوي بالدرونز": [
                "تعتبر طائرات الدرونز ثورة في عالم المسح الجوي، حيث توفر دقة عالية وسرعة في جمع البيانات بتكلفة أقل من الطرق التقليدية.",
                "من خلال استخدام كاميرات متخصصة وتقنيات مثل LiDAR، يمكن للدرونز إنشاء نماذج ثلاثية الأبعاد دقيقة للتضاريس والمباني.",
                "تتطلب عمليات المسح بالدرونز تخطيطًا دقيقًا للمسارات وتحديد نقاط التحكم الأرضية (GCPs) لضمان دقة النتائج النهائية.",
                "يتم معالجة الصور الملتقطة باستخدام برمجيات متخصصة مثل Pix4D أو Agisoft Metashape لإنتاج خرائط أورثوفوتوغرافية وسحب نقطية.",
            ],
            "كيفية استخدام أجهزة GPS في المشاريع الهندسية": [
                "أصبحت أجهزة استقبال GPS (نظام تحديد المواقع العالمي) أداة لا غنى عنها في المشاريع الهندسية الحديثة، من تحديد مواقع الأعمدة إلى مراقبة حركة الهياكل.",
                "تعتمد الدقة على نوع الجهاز المستخدم، فهناك أجهزة أحادية التردد وأخرى ثنائية التردد توفر دقة تصل إلى مستوى السنتيمتر باستخدام تقنيات مثل RTK.",
                "قبل البدء في أي مشروع، يجب التأكد من أن إعدادات الجهاز متوافقة مع نظام الإحداثيات المحلي للمشروع لتجنب الأخطاء المكلفة.",
            ],
            "مراجعة جهاز توتال ستيشن لايكا TS16": [
                "يُعد جهاز Leica TS16 من الأجهزة الرائدة في فئته، حيث يجمع بين الدقة الفائقة والبرمجيات الذكية التي تسهل العمل الميداني.",
                "يتميز الجهاز بتقنية ATRplus التي تتيح له تتبع الهدف (العاكس) بشكل تلقائي، مما يزيد من إنتاجية المساح بشكل كبير.",
                "واجهة المستخدم في برنامج Leica Captivate سهلة وبديهية، وتدعم العديد من التطبيقات المساحية مثل التوقيع والرفع المساحي وحساب الكميات.",
            ],
            "أساسيات عمل أجهزة الليزر سكانر ثلاثي الأبعاد": [
                "تعتمد أجهزة المسح بالليزر ثلاثي الأبعاد على إرسال ملايين النبضات الليزرية في الثانية وقياس زمن عودتها لإنشاء سحابة نقطية (Point Cloud) تمثل البيئة المحيطة بدقة.",
                "تُستخدم هذه التقنية في مجالات متنوعة مثل توثيق المباني الأثرية، ومراقبة التشوهات في المنشآت، وإنشاء نماذج As-Built للمصانع.",
                "بعد جمع البيانات، يتم استخدام برامج مثل Autodesk ReCap أو Trimble RealWorks لتنظيف السحابة النقطية واستخراج المعلومات الهندسية منها.",
            ],
            "تطبيقات نظم المعلومات الجغرافية (GIS) في التخطيط العمراني": [
                "تُعد نظم المعلومات الجغرافية (GIS) أداة قوية للمخططين العمرانيين، حيث تسمح بتحليل البيانات المكانية لاتخاذ قرارات مستنيرة.",
                "يمكن استخدام GIS لتحليل أفضل المواقع لإنشاء خدمات جديدة مثل المدارس والمستشفيات، بناءً على الكثافة السكانية وشبكات الطرق.",
                "تساعد الخرائط الموضوعية (Thematic Maps) التي يتم إنتاجها بواسطة GIS في عرض المعلومات المعقدة بطريقة بصرية سهلة الفهم لأصحاب المصلحة.",
            ],
        }
        blog_titles = list(blog_content_templates.keys())

        created_count = 0
        for i in range(total):
            # Select a title and its corresponding content template
            base_title = random.choice(blog_titles)
            title = f"{base_title} - الجزء {i + 1}"

            # Generate more relevant content
            content_paragraphs = blog_content_templates.get(base_title, [])
            # Add some generic paragraphs from Faker to make it longer
            for _ in range(random.randint(4, 8)):
                content_paragraphs.append(
                    fake.paragraph(nb_sentences=random.randint(3, 5))
                )
            random.shuffle(content_paragraphs)
            content = "\n\n".join(content_paragraphs)

            blog = Blog(
                author=author,
                title=title,
                content=content,
                is_published=True,
            )

            # Add image to the blog post
            with open(image_path, "rb") as f:
                # Use a unique name for each image file to avoid conflicts
                image_name = f"logo_{random.randint(1000, 9999)}.png"
                blog.image.save(image_name, File(f), save=False)

            blog.save()  # This will also generate the slug

            # Add some tags
            blog.tags.add("هندسة مساحة", "أجهزة مساحية", "تقنية")
            created_count += 1

            self.stdout.write(f"  - Created blog: '{blog.title}'")

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully created {created_count} blog posts.")
        )
