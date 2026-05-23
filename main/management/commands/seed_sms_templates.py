# -*- coding: utf-8 -*-
"""
Management command to seed SMSTemplate with default Arabic message bodies.

Usage:
    python manage.py seed_sms_templates               # insert new, skip existing
    python manage.py seed_sms_templates --overwrite   # replace all existing
    python manage.py seed_sms_templates --key order_shipped  # seed only one key
"""

from django.core.management.base import BaseCommand

# ---------------------------------------------------------------------------
# Template definitions
# Each entry: key, name, name_ar, body, available_variables
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "key": "order_created",
        "name": "Order Created SMS",
        "name_ar": "رسالة تأكيد الطلب",
        "body": (
            "{{site_name}}\n"
            "تم استلام طلبك رقم #{{order_number}} بنجاح.\n"
            "المبلغ الإجمالي: {{amount}} {{currency}}\n"
            "سنتواصل معك قريباً بتفاصيل الشحن."
        ),
        "available_variables": "{{order_number}}\n{{amount}}\n{{currency}}\n{{site_name}}",
    },
    {
        "key": "order_shipped",
        "name": "Order Shipped SMS",
        "name_ar": "رسالة شحن الطلب",
        "body": (
            "{{site_name}}\n"
            "طلبك رقم #{{order_number}} في الطريق إليك!\n"
            "تابع حالة الشحن من حسابك على الموقع."
        ),
        "available_variables": "{{order_number}}\n{{status}}\n{{site_name}}",
    },
    {
        "key": "order_delivered",
        "name": "Order Delivered SMS",
        "name_ar": "رسالة تسليم الطلب",
        "body": (
            "{{site_name}}\n"
            "تم تسليم طلبك رقم #{{order_number}} بنجاح.\n"
            "نشكرك على ثقتك بنا ونتطلع لخدمتك مجدداً."
        ),
        "available_variables": "{{order_number}}\n{{status}}\n{{site_name}}",
    },
    {
        "key": "order_cancelled",
        "name": "Order Cancelled SMS",
        "name_ar": "رسالة إلغاء الطلب",
        "body": (
            "{{site_name}}\n"
            "تم إلغاء طلبك رقم #{{order_number}} بسبب انتهاء مهلة الدفع.\n"
            "المبلغ: {{amount}} {{currency}}\n"
            "للاستفسار تواصل معنا عبر الموقع."
        ),
        "available_variables": "{{order_number}}\n{{amount}}\n{{currency}}\n{{site_name}}",
    },
    {
        "key": "order_paid",
        "name": "Payment Confirmed SMS",
        "name_ar": "رسالة تأكيد الدفع الكامل",
        "body": (
            "{{site_name}}\n"
            "تم استلام دفعتك الكاملة لطلب رقم #{{order_number}}.\n"
            "المبلغ: {{amount}} {{currency}}\n"
            "شكراً لك!"
        ),
        "available_variables": "{{order_number}}\n{{amount}}\n{{currency}}\n{{site_name}}",
    },
    {
        "key": "order_partial_payment",
        "name": "Partial Payment SMS",
        "name_ar": "رسالة الدفعة الجزئية",
        "body": (
            "{{site_name}}\n"
            "تم استلام دفعة جزئية لطلبك رقم #{{order_number}}.\n"
            "المبلغ المدفوع: {{paid}}\n"
            "المبلغ المتبقي: {{remaining}}\n"
            "يرجى إتمام الدفع من حسابك على الموقع."
        ),
        "available_variables": "{{order_number}}\n{{paid}}\n{{remaining}}\n{{site_name}}",
    },
]


class Command(BaseCommand):
    help = (
        "Seed SMSTemplate with default Arabic message bodies.\n"
        "  --overwrite  Replace body of existing templates\n"
        "  --key KEY    Seed only the specified template key"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Overwrite existing templates (default: skip existing)",
        )
        parser.add_argument(
            "--key",
            type=str,
            default=None,
            help="Seed only a specific template key",
        )

    def handle(self, *args, **options):
        from main.models import SMSTemplate

        overwrite = options["overwrite"]
        only_key = options.get("key")

        templates_to_seed = TEMPLATES
        if only_key:
            templates_to_seed = [t for t in TEMPLATES if t["key"] == only_key]
            if not templates_to_seed:
                self.stdout.write(self.style.ERROR(f"No template found for key: '{only_key}'"))
                self.stdout.write("Available keys: " + ", ".join(t["key"] for t in TEMPLATES))
                return

        created_count = updated_count = skipped_count = 0

        for data in templates_to_seed:
            key = data["key"]
            existing = SMSTemplate.objects.filter(key=key).first()

            if existing:
                if overwrite:
                    for field, value in data.items():
                        if field != "key":
                            setattr(existing, field, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"  ↻  Updated : {key}"))
                else:
                    skipped_count += 1
                    self.stdout.write(f"  –  Skipped : {key}  (already exists, use --overwrite to replace)")
            else:
                SMSTemplate.objects.create(**data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓  Created : {key}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done — created: {created_count}, updated: {updated_count}, skipped: {skipped_count}"
        ))
