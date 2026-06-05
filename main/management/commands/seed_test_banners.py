"""
Management command: seed_test_banners
Creates BannerSlot records + multiple PaidBanners per slot (3 per slot)
so the auto-rotation mechanism can be tested visually.

Usage:
    python manage.py seed_test_banners            # create slots + test banners
    python manage.py seed_test_banners --clear     # delete all [TEST] banners and slots
    python manage.py seed_test_banners --reset     # clear then re-create
"""

import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

TEST_MARKER = "[TEST]"

# ── BannerSlot definitions ───────────────────────────────────────────────────
# (slot_key, name_ar, ad_type, max_capacity, rotation_seconds)
SLOT_SPECS = [
    ("homepage-banner",   "بانر الرئيسية",          "banner",      3, 5),
    ("homepage-sidebar",  "إعلان جانبي الرئيسية",   "sidebar",     3, 7),
    ("homepage-featured", "صندوق مميز الرئيسية",    "featured_box", 2, 8),
]

# ── Banner specs: one row per banner ─────────────────────────────────────────
# (slot_key_or_None, ad_type, title_ar, company_ar, dw, dh, mw, mh, bg, fg)
BANNER_SPECS = [
    # ── homepage-banner slot: 3 advertisers ──────────────────────────────────
    ("homepage-banner", "banner", "بانر عميل أ - شركة الأمل",    "شركة الأمل",
     970, 150, 320, 50, "#1e3a5f", "#f0e6ff"),
    ("homepage-banner", "banner", "بانر عميل ب - مؤسسة النور",   "مؤسسة النور",
     970, 150, 320, 50, "#7b2000", "#fce4ec"),
    ("homepage-banner", "banner", "بانر عميل ج - متجر الأصيل",   "متجر الأصيل",
     970, 150, 320, 50, "#1a5f3a", "#d8f3dc"),

    # ── homepage-sidebar slot: 3 advertisers ─────────────────────────────────
    ("homepage-sidebar", "sidebar", "جانبي عميل أ - شركة الأمل",  "شركة الأمل",
     300, 250, None, None, "#2d6a4f", "#d8f3dc"),
    ("homepage-sidebar", "sidebar", "جانبي عميل ب - مؤسسة النور", "مؤسسة النور",
     300, 250, None, None, "#b5451b", "#fff3e0"),
    ("homepage-sidebar", "sidebar", "جانبي عميل ج - متجر الأصيل", "متجر الأصيل",
     300, 250, None, None, "#4a1a7b", "#f3e4fc"),

    # ── homepage-featured slot: 2 advertisers ────────────────────────────────
    ("homepage-featured", "featured_box", "مميز عميل أ - شركة الأمل",  "شركة الأمل",
     970, 250, None, None, "#7b2d8b", "#fce4ec"),
    ("homepage-featured", "featured_box", "مميز عميل ب - مؤسسة النور", "مؤسسة النور",
     970, 250, None, None, "#1a5040", "#d8f3dc"),

    # ── popup: standalone (no slot) ──────────────────────────────────────────
    (None, "popup", "نافذة شركة الأمل", "شركة الأمل",
     300, 250, None, None, "#b5451b", "#fff3e0"),
]


def _make_image(width, height, bg_color, text_color, label, size_str, company=""):
    """Generate a colorful PNG placeholder image using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    margin = max(3, min(width, height) // 20)
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=text_color, width=max(1, margin // 2),
    )

    try:
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                        max(10, min(width, height) // 6))
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                        max(8, min(width, height) // 10))
    except Exception:
        font_big = font_small = ImageFont.load_default()

    cx, cy = width // 2, height // 2
    bbox = draw.textbbox((0, 0), size_str, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), size_str, fill=text_color, font=font_big)

    if company:
        bbox2 = draw.textbbox((0, 0), company, font=font_small)
        tw2, th2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text((cx - tw2 // 2, cy + th // 2 + max(3, height // 15)),
                  company, fill=text_color, font=font_small)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()


class Command(BaseCommand):
    help = "Seed BannerSlots + test PaidBanner records for rotation testing"

    def add_arguments(self, parser):
        parser.add_argument("--clear",  action="store_true",
                            help="Delete all [TEST] banners and slots")
        parser.add_argument("--reset",  action="store_true",
                            help="Clear then re-create (same as --clear + run)")
        parser.add_argument("--country", default="SA",
                            help="Country code (default: SA)")

    def handle(self, *args, **options):
        from main.models import PaidBanner, BannerSlot
        from content.models import Country
        from django.contrib.auth import get_user_model
        User = get_user_model()

        do_clear  = options["clear"] or options["reset"]
        do_create = not options["clear"] or options["reset"]

        if do_clear:
            deleted_b, _ = PaidBanner.objects.filter(title__startswith=TEST_MARKER).delete()
            deleted_s, _ = BannerSlot.objects.filter(name__startswith=TEST_MARKER).delete()
            self.stdout.write(self.style.WARNING(
                f"Deleted {deleted_b} test banner(s) and {deleted_s} test slot(s)."
            ))
            if not do_create:
                return

        if not do_create:
            return

        # ── Resolve country ────────────────────────────────────────────────
        country_code = options["country"]
        try:
            country = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            country = Country.objects.filter(is_active=True).first()
            if not country:
                self.stderr.write("No active country found.")
                return
        self.stdout.write(f"Country: {country.name} ({country.code})")

        # ── Resolve advertiser ────────────────────────────────────────────
        advertiser = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not advertiser:
            self.stderr.write("No user found. Create a superuser first.")
            return
        self.stdout.write(f"Advertiser: {advertiser.username}")

        # ── Create BannerSlot records ─────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("--- BannerSlots ---")
        for slot_key, name_ar, ad_type, max_cap, rot_s in SLOT_SPECS:
            slot, created = BannerSlot.objects.get_or_create(
                slot_key=slot_key,
                defaults={
                    "name": f"{TEST_MARKER} {name_ar}",
                    "name_ar": f"{TEST_MARKER} {name_ar}",
                    "ad_type": ad_type,
                    "max_capacity": max_cap,
                    "rotation_seconds": rot_s,
                    "is_active": True,
                }
            )
            if not created:
                # Update rotation settings in case they changed
                slot.rotation_seconds = rot_s
                slot.max_capacity = max_cap
                slot.is_active = True
                slot.save(update_fields=["rotation_seconds", "max_capacity", "is_active"])
            verb = "created" if created else "exists"
            self.stdout.write(self.style.SUCCESS(
                f"  slot [{slot_key}] {verb} — max={max_cap} rot={rot_s}s"
            ))

        # ── Create PaidBanner records ─────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("--- PaidBanners ---")
        now   = timezone.now()
        start = now - timedelta(days=1)
        end   = now + timedelta(days=365)
        created_count = 0

        for slot_key, ad_type, title_ar, company_ar, dw, dh, mw, mh, bg, fg in BANNER_SPECS:
            full_title = f"{TEST_MARKER} {title_ar}"

            # Skip if exact title already exists
            if PaidBanner.objects.filter(title=full_title).exists():
                self.stdout.write(f"  ↩  {full_title!r}: already exists, skipping.")
                continue

            banner = PaidBanner(
                title=full_title,
                title_ar=full_title,
                description=f"بانر تجريبي للتناوب — {company_ar}",
                description_ar=f"بانر تجريبي للتناوب — {company_ar}",
                advertiser=advertiser,
                company_name=company_ar,
                target_url="https://example.com",
                cta_text="اعرف المزيد",
                cta_text_ar="اعرف المزيد",
                open_in_new_tab=True,
                ad_type=ad_type,
                advertising_space=slot_key,
                placement_type=PaidBanner.PlacementType.GENERAL,
                country=country,
                start_date=start,
                end_date=end,
                status=PaidBanner.Status.ACTIVE,
                is_active=True,
                price=0,
                currency="EGP",
                payment_status="paid",
            )

            size_str = f"{dw}x{dh}"
            desktop_bytes = _make_image(dw, dh, bg, fg, size_str, size_str, company_ar)
            banner.image.save(
                f"test_{ad_type}_{dw}x{dh}_{company_ar[:4]}.png",
                ContentFile(desktop_bytes), save=False,
            )

            if mw and mh:
                mobile_bytes = _make_image(mw, mh, bg, fg, f"{mw}x{mh}", f"{mw}x{mh}", company_ar)
                banner.mobile_image.save(
                    f"test_{ad_type}_mob_{mw}x{mh}_{company_ar[:4]}.png",
                    ContentFile(mobile_bytes), save=False,
                )

            try:
                banner.save()
                created_count += 1
                slot_info = f"[{slot_key}]" if slot_key else "[no-slot]"
                self.stdout.write(self.style.SUCCESS(
                    f"  + {slot_info} {ad_type}: {full_title!r} (id={banner.pk})"
                ))
            except Exception as exc:
                self.stderr.write(f"  ✗  Failed: {full_title!r}: {exc}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created_count} new banner(s)."
        ))
        self.stdout.write(
            "To remove:  python manage.py seed_test_banners --clear"
        )
        self.stdout.write(
            "To reset:   python manage.py seed_test_banners --reset"
        )
