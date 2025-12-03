from django.core.management.base import BaseCommand
from main.models import ClassifiedAd
from django.contrib.auth import get_user_model
from content.models import Country


class Command(BaseCommand):
    help = "Test classified ad description sanitization"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        author = User.objects.first()

        if not author:
            self.stdout.write(
                self.style.ERROR("No users found. Cannot create test ad.")
            )
            return

        # Get first active country
        country = Country.objects.filter(is_active=True).first()
        if not country:
            self.stdout.write(self.style.ERROR("No active countries found."))
            return

        # Get first category
        from main.models import Category

        category = Category.objects.filter(parent__isnull=False).first()
        if not category:
            self.stdout.write(self.style.ERROR("No categories found."))
            return

        # Create test ad with dangerous content
        dangerous_content = """
        <h2>وصف المنتج</h2>
        <p>This is a product description.</p>
        <script>
        let counter = 0;
        function addPoint(x="", y="") {
            counter++;
            alert("This should be removed!");
        }
        drawShape();
        </script>
        <button onclick="alert('danger')">اضغط هنا</button>
        <iframe src="https://evil.com"></iframe>
        <p onload="alert('loaded')">المزيد من المحتوى</p>
        <div style="background: red;">نص عادي</div>
        """

        ad = ClassifiedAd(
            user=author,
            category=category,
            title="Security Test Ad",
            description=dangerous_content,
            price=100.00,
            country=country,
            status=ClassifiedAd.AdStatus.DRAFT,
        )
        ad.save()

        self.stdout.write(f"\nCreated test ad ID: {ad.id}")
        self.stdout.write("\nOriginal description length: " + str(len(ad.description)))
        self.stdout.write("\nOriginal description contains:")
        self.stdout.write(f'  <script>: {"✗" if "<script>" in ad.description else "✓"}')
        self.stdout.write(f'  onclick: {"✗" if "onclick" in ad.description else "✓"}')
        self.stdout.write(f'  <iframe>: {"✗" if "<iframe>" in ad.description else "✓"}')
        self.stdout.write(f'  onload: {"✗" if "onload" in ad.description else "✓"}')

        safe_content = ad.get_safe_description()

        self.stdout.write("\n\nSanitized description length: " + str(len(safe_content)))
        self.stdout.write("\nSanitized description contains:")
        self.stdout.write(
            f'  <script>: {self.style.ERROR("✗ FAIL") if "<script>" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  onclick: {self.style.ERROR("✗ FAIL") if "onclick" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  <iframe>: {self.style.ERROR("✗ FAIL") if "<iframe>" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  onload: {self.style.ERROR("✗ FAIL") if "onload" in safe_content else self.style.SUCCESS("✓ REMOVED")}'
        )
        self.stdout.write(
            f'  style attribute: {self.style.SUCCESS("✓ PRESERVED") if "style=" in safe_content else "✗ REMOVED"}'
        )

        self.stdout.write("\n\nSanitized description:")
        self.stdout.write(safe_content)

        # Clean up
        ad.delete()
        self.stdout.write(self.style.SUCCESS("\n\nTest ad deleted."))
