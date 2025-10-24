from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django_filters.views import FilterView

from .filters import ClassifiedAdFilter
from .forms import AdImageFormSet, ClassifiedAdForm
from .models import AdImage, AdPackage, Category, ClassifiedAd, User, UserPackage


class ClassifiedAdListView(FilterView):
    """
    A view for listing and filtering classified ads.
    """

    model = ClassifiedAd
    filterset_class = ClassifiedAdFilter
    template_name = "classifieds/ad_list.html"
    context_object_name = "ads"
    paginate_by = 12

    def get_queryset(self):
        # Start with only active ads
        queryset = (
            ClassifiedAd.objects.filter(status=ClassifiedAd.AdStatus.ACTIVE)
            .select_related("user", "category", "country")
            .prefetch_related("images", "features")
        )
        return queryset


class MyClassifiedAdsView(LoginRequiredMixin, ListView):
    """View to list the current user's classified ads."""

    model = ClassifiedAd
    template_name = "classifieds/my_ads_list.html"
    context_object_name = "ads"

    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class ClassifiedAdCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user has an active package with remaining ads before allowing
        them to access the creation form.
        """
        user = self.request.user
        active_package = UserPackage.objects.filter(
            user=user, ads_remaining__gt=0, expiry_date__gte=timezone.now()
        ).first()

        if not active_package:
            # If no active package, check if a default package should be assigned (for new users)
            if not UserPackage.objects.filter(user=user).exists():
                default_package = AdPackage.objects.filter(
                    is_default=True, is_active=True
                ).first()
                if default_package:
                    UserPackage.objects.create(user=user, package=default_package)
                    messages.info(
                        request,
                        _(
                            "لقد تم منحك الباقة الافتراضية المجانية! يمكنك الآن نشر إعلانك الأول."
                        ),
                    )
                    return super().dispatch(request, *args, **kwargs)

            messages.error(
                request,
                _("لقد استنفدت رصيدك من الإعلانات. يرجى شراء باقة جديدة للمتابعة."),
            )
            # In a real application, you would redirect to a 'purchase-package' page.
            # For now, we redirect to the 'my_ads' list.
            return redirect("main:my_ads")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST, self.request.FILES, prefix="images"
            )
        else:
            # Limit extra forms to 5 as requested
            AdImageFormSet.extra = 5
            context["image_formset"] = AdImageFormSet(
                prefix="images", queryset=AdImage.objects.none()
            )

        context["ad_categories"] = Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED, is_active=True
        )
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Auto-approve ads for verified users
        if self.request.user.verification_status == User.VerificationStatus.VERIFIED:
            form.instance.status = ClassifiedAd.AdStatus.ACTIVE
            messages.success(
                self.request, _("إعلانك نشط الآن لأنه تم التحقق من حسابك.")
            )
        else:
            form.instance.status = ClassifiedAd.AdStatus.PENDING
            messages.info(self.request, _("تم إرسال إعلانك للمراجعة وسيتم نشره قريباً."))

        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()

            # Decrement ad count from user's package
            active_package = (
                UserPackage.objects.filter(user=self.request.user, ads_remaining__gt=0)
                .order_by("expiry_date")
                .first()
            )
            if active_package:
                active_package.use_ad()

            return redirect("main:ad_create_success", pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ClassifiedAdUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing classified ad."""

    model = ClassifiedAd
    form_class = ClassifiedAdForm
    template_name = "classifieds/ad_form.html"
    success_url = reverse_lazy("main:my_ads")

    def get_queryset(self):
        # Ensure users can only edit their own ads
        return ClassifiedAd.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = AdImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="images",
            )
        else:
            # Limit extra forms to 5
            AdImageFormSet.extra = 5 - self.object.images.count()
            context["image_formset"] = AdImageFormSet(
                instance=self.object, prefix="images", queryset=self.object.images.all()
            )
        context["ad_categories"] = Category.objects.filter(
            section_type=Category.SectionType.CLASSIFIED, is_active=True
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.save()
            messages.success(self.request, _("تم تحديث الإعلان بنجاح!"))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ClassifiedAdCreateSuccessView(LoginRequiredMixin, DetailView):
    """
    Shows a success message after creating an ad and suggests upgrades.
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_create_success.html"
    context_object_name = "ad"

    def get_queryset(self):
        return ClassifiedAd.objects.filter(user=self.request.user)


class ClassifiedAdDetailView(DetailView):
    """
    Public view for a single classified ad.
    """

    model = ClassifiedAd
    template_name = "classifieds/ad_detail.html"
    context_object_name = "ad"

    def get_queryset(self):
        # Only show active ads to the public
        return ClassifiedAd.objects.filter(status=ClassifiedAd.AdStatus.ACTIVE)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count without causing a race condition
        ClassifiedAd.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        # obj.refresh_from_db() # The template will display the updated count
        return obj
