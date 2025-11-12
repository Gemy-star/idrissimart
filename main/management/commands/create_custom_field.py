from django.core.management.base import BaseCommand, CommandError
from main.models import CustomField, Category

class Command(BaseCommand):
    help = 'Creates a new custom field for a given category.'

    def add_arguments(self, parser):
        parser.add_argument('category_id', type=int, help='The ID of the category to add the field to.')
        parser.add_argument('field_name', type=str, help='The internal name of the field (e.g., "year_of_manufacture").')
        parser.add_argument('label_ar', type=str, help='The Arabic label for the field (e.g., "سنة الصنع").')
        parser.add_argument(
            '--type',
            type=str,
            default='text',
            choices=[choice[0] for choice in CustomField.FieldType.choices],
            help='The field type. Choose from: ' + ', '.join([choice[0] for choice in CustomField.FieldType.choices])
        )
        parser.add_argument('--required', action='store_true', help='Mark the field as required.')
        parser.add_argument('--order', type=int, default=0, help='The display order of the field.')

    def handle(self, *args, **options):
        category_id = options['category_id']
        field_name = options['field_name']
        label_ar = options['label_ar']
        field_type = options['type']
        is_required = options['required']
        order = options['order']

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise CommandError(f'Category with ID "{category_id}" does not exist.')

        if CustomField.objects.filter(category=category, name=field_name).exists():
            raise CommandError(f'Custom field with name "{field_name}" already exists for this category.')

        field = CustomField.objects.create(
            category=category,
            name=field_name,
            label_ar=label_ar,
            field_type=field_type,
            is_required=is_required,
            order=order,
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created custom field "{field.name}" for category "{category.name}".'))
