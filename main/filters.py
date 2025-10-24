import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Category, ClassifiedAd


class ClassifiedAdFilter(django_filters.FilterSet):
    """
    FilterSet for ClassifiedAd model.
    """

    title = django_filters.CharFilter(lookup_expr="icontains", label=_("بحث بالاسم"))
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED, is_active=True
        ),
        label=_("القسم"),
    )
    subcategory = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED,
            is_active=True,
            parent__isnull=False,
        ),
        label=_("الفئة الفرعية"),
    )
    city = django_filters.CharFilter(lookup_expr="icontains", label=_("المدينة"))
    brand = django_filters.CharFilter(
        field_name="custom_fields__brand", lookup_expr="icontains", label=_("الماركة")
    )
    condition = django_filters.ChoiceFilter(
        field_name="custom_fields__condition",
        choices=[
            ("new", _("جديد")),
            ("used", "مستعمل - كالجديد"),
            ("used_good", "مستعمل - جيد"),
        ],
        label=_("الحالة"),
    )
    price = django_filters.RangeFilter(label=_("نطاق السعر"))

    order_by = django_filters.OrderingFilter(
        fields=(
            ("price", "price"),
            ("-price", "price_desc"),
            ("views_count", "views"),
            ("-views_count", "views_desc"),
        ),
        field_labels={
            "price": _("السعر (من الأقل للأعلى)"),
            "price_desc": _("السعر (من الأعلى للأقل)"),
            "views_desc": _("الأكثر مشاهدة"),
        },
        label=_("ترتيب حسب"),
    )

    class Meta:
        model = ClassifiedAd
        fields = [
            "title",
            "category",
            "subcategory",
            "city",
            "price",
            "brand",
            "condition",
        ]
