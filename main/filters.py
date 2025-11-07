import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Category, ClassifiedAd


class ClassifiedAdFilter(django_filters.FilterSet):
    """
    Enhanced FilterSet for ClassifiedAd model with comprehensive filtering options.
    """

    # Text search
    search = django_filters.CharFilter(method="filter_search", label=_("البحث"))

    # Category filtering
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

    # Location filtering
    city = django_filters.CharFilter(lookup_expr="icontains", label=_("المدينة"))

    # Price range filtering
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label=_("السعر من")
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label=_("السعر إلى")
    )

    # Brand/Type filtering (dynamic based on category)
    brand = django_filters.CharFilter(
        field_name="custom_fields__brand", lookup_expr="icontains", label=_("الماركة")
    )
    book_type = django_filters.CharFilter(
        field_name="custom_fields__book_type",
        lookup_expr="icontains",
        label=_("نوع الكتاب"),
    )
    program_type = django_filters.CharFilter(
        field_name="custom_fields__program_type",
        lookup_expr="icontains",
        label=_("نوع البرنامج"),
    )

    # Condition filtering
    condition = django_filters.ChoiceFilter(
        field_name="custom_fields__condition",
        choices=[
            ("new", _("جديد")),
            ("used_excellent", "مستعمل - ممتاز"),
            ("used_good", "مستعمل - جيد"),
            ("used_fair", "مستعمل - مقبول"),
        ],
        label=_("الحالة"),
    )

    # Feature-based filtering
    is_negotiable = django_filters.BooleanFilter(label=_("قابل للتفاوض"))
    is_delivery_available = django_filters.BooleanFilter(label=_("التوصيل متاح"))
    is_featured = django_filters.BooleanFilter(label=_("إعلانات مميزة"))

    # Verification filtering
    verified_only = django_filters.BooleanFilter(
        method="filter_verified_users", label=_("أعضاء موثقين فقط")
    )
    company_only = django_filters.BooleanFilter(
        method="filter_company_users", label=_("شركات موثقة فقط")
    )

    # Enhanced sorting options
    order_by = django_filters.OrderingFilter(
        fields=(
            ("-created_at", "newest"),
            ("created_at", "oldest"),
            ("price", "price_low"),
            ("-price", "price_high"),
            ("-views_count", "most_viewed"),
            ("views_count", "least_viewed"),
            ("title", "title_asc"),
            ("-title", "title_desc"),
            ("-is_featured", "featured_first"),
        ),
        field_labels={
            "newest": _("الأحدث"),
            "oldest": _("الأقدم"),
            "price_low": _("السعر (من الأقل للأعلى)"),
            "price_high": _("السعر (من الأعلى للأقل)"),
            "most_viewed": _("الأكثر مشاهدة"),
            "least_viewed": _("الأقل مشاهدة"),
            "title_asc": _("العنوان (أ-ي)"),
            "title_desc": _("العنوان (ي-أ)"),
            "featured_first": _("المميزة أولاً"),
        },
        label=_("ترتيب حسب"),
    )

    def filter_search(self, queryset, name, value):
        """Enhanced search functionality"""
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
                | Q(custom_fields__brand__icontains=value)
                | Q(custom_fields__book_type__icontains=value)
                | Q(custom_fields__program_type__icontains=value)
            )
        return queryset

    def filter_verified_users(self, queryset, name, value):
        """Filter for verified users only"""
        if value:
            return queryset.filter(user__verification_status="verified")
        return queryset

    def filter_company_users(self, queryset, name, value):
        """Filter for verified companies only"""
        if value:
            return queryset.filter(
                user__verification_status="verified", user__rank="company"
            )
        return queryset

    class Meta:
        model = ClassifiedAd
        fields = [
            "search",
            "category",
            "subcategory",
            "city",
            "min_price",
            "max_price",
            "brand",
            "book_type",
            "program_type",
            "condition",
            "is_negotiable",
            "is_delivery_available",
            "is_featured",
            "verified_only",
            "company_only",
            "order_by",
        ]
