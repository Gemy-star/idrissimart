import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Category, ClassifiedAd
from content.models import Country


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
    country = django_filters.ModelChoiceFilter(
        field_name="country",
        queryset=Country.objects.filter(is_active=True).order_by("order", "name"),
        label=_("الدولة"),
        empty_label=_("جميع الدول"),
    )
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
    is_featured = django_filters.BooleanFilter(
        field_name="is_highlighted", label=_("إعلانات مميزة")
    )
    is_urgent = django_filters.BooleanFilter(label=_("إعلانات عاجلة"))
    is_pinned = django_filters.BooleanFilter(label=_("إعلانات مثبتة"))

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
            ("-is_pinned", "pinned_first"),
            ("-is_urgent", "urgent_first"),
            ("-is_highlighted", "featured_first"),
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
            "pinned_first": _("المثبتة أولاً"),
            "urgent_first": _("العاجلة أولاً"),
            "featured_first": _("المميزة أولاً"),
        },
        label=_("ترتيب حسب"),
    )

    # ------------------------------------------------------------------
    # Arabic text normalisation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_arabic(text: str) -> str:
        """
        Normalise Arabic text so that variant forms of the same letter
        match each other:
          - Alef variants  (أ إ آ ٱ) → ا
          - Teh marbuta    (ة)        → ه
          - Yeh variants   (ى)        → ي
          - Strip tashkeel (diacritics / harakat)
        """
        import re
        # Remove diacritics (tashkeel / harakat)
        text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
        # Normalize alef variants → bare alef
        text = re.sub(r'[أإآٱ]', 'ا', text)
        # Normalize alef wasla
        text = text.replace('\u0671', 'ا')
        # Normalize teh marbuta → heh
        text = text.replace('ة', 'ه')
        # Normalize alef maqsura → yeh
        text = text.replace('ى', 'ي')
        return text

    def filter_search(self, queryset, name, value):
        """
        Comprehensive search across all meaningful fields:
          • title (AR/EN)
          • description
          • city / address
          • ALL custom field values (entire JSON blob)
          • publisher username / full name / company name
          • category name (AR/EN)

        Arabic text is normalised before matching so that users who type
        without diacritics, or use different alef forms (أ/إ/آ/ا), still
        get relevant results.
        """
        if not value:
            return queryset

        term = value.strip()
        norm = self._normalize_arabic(term)

        def make_q(t):
            """Build the Q tree for a given search term *t*."""
            return (
                # ── Core ad fields ─────────────────────────────────────────
                Q(title__icontains=t)
                | Q(description__icontains=t)
                # ── Location ───────────────────────────────────────────────
                | Q(city__icontains=t)
                | Q(address__icontains=t)
                # ── All custom-field values (searches raw JSON blob) ───────
                | Q(custom_fields__icontains=t)
                # ── Publisher identity ─────────────────────────────────────
                | Q(user__username__icontains=t)
                | Q(user__first_name__icontains=t)
                | Q(user__last_name__icontains=t)
                | Q(user__company_name__icontains=t)
                # ── Category ───────────────────────────────────────────────
                | Q(category__name__icontains=t)
                | Q(category__name_ar__icontains=t)
            )

        combined = make_q(term)

        # If normalisation produced a different string, also search that form
        if norm != term:
            combined |= make_q(norm)

        return queryset.filter(combined).distinct()

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

    def filter_queryset(self, queryset):
        """Override to apply dynamic custom field filters"""
        queryset = super().filter_queryset(queryset)

        # Apply custom field filters from request GET params
        for key, value in self.request.GET.items():
            if key.startswith('cf_') and value:
                field_name = key[3:]  # Remove 'cf_' prefix
                # Apply filter based on field type (handle both exact and contains)
                queryset = queryset.filter(
                    Q(**{f'custom_fields__{field_name}': value}) |
                    Q(**{f'custom_fields__{field_name}__icontains': value})
                )

        return queryset

    class Meta:
        model = ClassifiedAd
        fields = [
            "search",
            "category",
            "subcategory",
            "country",
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
            "is_urgent",
            "is_pinned",
            "verified_only",
            "company_only",
            "order_by",
        ]
