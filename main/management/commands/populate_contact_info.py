from django.core.management.base import BaseCommand

from main.models import ContactInfo


class Command(BaseCommand):
    help = "Populate contact information for the platform"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting contact info population..."))

        # Delete existing contact info to avoid duplicates
        ContactInfo.objects.all().delete()

        # Create the contact information
        contact_info = ContactInfo.objects.create(
            phone="+20 11 27078236",
            email="info@idrissimart.com",
            address="القاهرة، مصر",
            working_hours="السبت - الخميس، 9:00 ص - 5:00 م",
            whatsapp="+20 11 27078236",
            google_maps_link="https://maps.app.goo.gl/VHsHKhfZeAiec38z5?g_st=awb",
            map_embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d220834.08041339024!2d31.103695!3d30.0444196!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14583fa60b21beeb%3A0x79dfb296e8423bba!2sCairo%2C%20Cairo%20Governorate%2C%20Egypt!5e0!3m2!1sen!2s!4v1697630000000!5m2!1sen!2s",
            facebook="https://facebook.com/idrissimart",
            twitter="https://twitter.com/idrissimart",
            instagram="https://instagram.com/idrissimart",
            linkedin="https://linkedin.com/company/idrissimart",
            is_active=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Contact info created successfully!\n"
                f"   Phone: {contact_info.phone}\n"
                f"   Email: {contact_info.email}\n"
                f"   Address: {contact_info.address}\n"
                f"   Google Maps: {contact_info.google_maps_link}\n"
                f"   WhatsApp: {contact_info.whatsapp}"
            )
        )
