"""
Admin views for content management (HomeSlider, etc.)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from content.models import HomeSlider, Country, Blog, BlogCategory
from content.site_config import ContactPage, AboutPage, HomePage, SiteConfiguration


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


# ============================================
# HOME SLIDER MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_home_sliders(request):
    """List all home sliders"""
    sliders = (
        HomeSlider.objects.select_related("country")
        .all()
        .order_by("order", "-created_at")
    )

    # Filter by country if specified
    country_filter = request.GET.get("country")
    if country_filter:
        sliders = sliders.filter(country__code=country_filter)

    # Pagination
    paginator = Paginator(sliders, 20)
    page = request.GET.get("page", 1)
    sliders_page = paginator.get_page(page)

    context = {
        "sliders": sliders_page,
        "total_sliders": sliders.count(),
        "active_sliders": sliders.filter(is_active=True).count(),
        "inactive_sliders": sliders.filter(is_active=False).count(),
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
        "selected_country": country_filter,
    }

    return render(request, "admin_dashboard/home_sliders/list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_create(request):
    """Create new home slider"""
    if request.method == "POST":
        try:
            # Get country (optional)
            country_id = request.POST.get("country")
            country = None
            if country_id:
                country = get_object_or_404(Country, id=country_id)

            slider = HomeSlider.objects.create(
                country=country,
                title=request.POST.get("title", ""),
                title_ar=request.POST.get("title_ar", ""),
                subtitle=request.POST.get("subtitle", ""),
                subtitle_ar=request.POST.get("subtitle_ar", ""),
                description=request.POST.get("description", ""),
                description_ar=request.POST.get("description_ar", ""),
                button_text=request.POST.get("button_text", ""),
                button_text_ar=request.POST.get("button_text_ar", ""),
                button_url=request.POST.get("button_url", ""),
                background_color=request.POST.get("background_color", "#4B315E"),
                text_color=request.POST.get("text_color", "#FFFFFF"),
                order=int(request.POST.get("order", 0)),
                is_active=request.POST.get("is_active") == "on",
            )

            # Handle image upload
            if "image" in request.FILES:
                slider.image = request.FILES["image"]
                slider.save()

            messages.success(request, _("تم إنشاء الشريحة بنجاح"))
            return redirect("main:admin_home_sliders")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "action": "create",
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
    }

    return render(request, "admin_dashboard/home_sliders/form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_edit(request, slider_id):
    """Edit home slider"""
    slider = get_object_or_404(HomeSlider, id=slider_id)

    if request.method == "POST":
        try:
            # Update country (optional)
            country_id = request.POST.get("country")
            if country_id:
                slider.country = get_object_or_404(Country, id=country_id)
            else:
                slider.country = None

            slider.title = request.POST.get("title", "")
            slider.title_ar = request.POST.get("title_ar", "")
            slider.subtitle = request.POST.get("subtitle", "")
            slider.subtitle_ar = request.POST.get("subtitle_ar", "")
            slider.description = request.POST.get("description", "")
            slider.description_ar = request.POST.get("description_ar", "")
            slider.button_text = request.POST.get("button_text", "")
            slider.button_text_ar = request.POST.get("button_text_ar", "")
            slider.button_url = request.POST.get("button_url", "")
            slider.background_color = request.POST.get("background_color", "#4B315E")
            slider.text_color = request.POST.get("text_color", "#FFFFFF")
            slider.order = int(request.POST.get("order", 0))
            slider.is_active = request.POST.get("is_active") == "on"

            # Handle image upload
            if "image" in request.FILES:
                slider.image = request.FILES["image"]

            slider.save()

            messages.success(request, _("تم تحديث الشريحة بنجاح"))
            return redirect("main:admin_home_sliders")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "slider": slider,
        "action": "edit",
        "countries": Country.objects.filter(is_active=True).order_by("order", "name"),
    }

    return render(request, "admin_dashboard/home_sliders/form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_home_slider_delete(request, slider_id):
    """Delete home slider"""
    slider = get_object_or_404(HomeSlider, id=slider_id)

    if request.method == "POST":
        slider.delete()
        messages.success(request, _("تم حذف الشريحة بنجاح"))

    return redirect("main:admin_home_sliders")


@login_required
@user_passes_test(is_admin)
def admin_home_slider_toggle(request, slider_id):
    """Toggle slider active status"""
    slider = get_object_or_404(HomeSlider, id=slider_id)
    slider.is_active = not slider.is_active
    slider.save()

    status = _("مفعّل") if slider.is_active else _("معطّل")
    messages.success(request, f"تم تغيير حالة الشريحة إلى: {status}")

    return redirect("main:admin_home_sliders")


# ============================================
# SITE CONTENT PAGES MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_site_content(request):
    """Site content management dashboard"""
    context = {
        "contact_page": ContactPage.get_solo(),
        "about_page": AboutPage.get_solo(),
        "home_page": HomePage.get_solo(),
        "site_config": SiteConfiguration.get_solo(),
    }
    return render(request, "admin_dashboard/site_content.html", context)


@login_required
@user_passes_test(is_admin)
def admin_edit_contactpage(request):
    """Edit contact page"""
    contact_page = ContactPage.get_solo()

    if request.method == "POST":
        try:
            # Update basic fields
            contact_page.title = request.POST.get("title", "")
            contact_page.title_ar = request.POST.get("title_ar", "")
            contact_page.description = request.POST.get("description", "")
            contact_page.description_ar = request.POST.get("description_ar", "")

            # Form settings
            contact_page.enable_contact_form = (
                request.POST.get("enable_contact_form") == "on"
            )
            contact_page.notification_email = request.POST.get("notification_email", "")

            # Display settings
            contact_page.show_phone = request.POST.get("show_phone") == "on"
            contact_page.show_address = request.POST.get("show_address") == "on"
            contact_page.show_office_hours = (
                request.POST.get("show_office_hours") == "on"
            )
            contact_page.show_map = request.POST.get("show_map") == "on"

            # Office hours
            contact_page.office_hours = request.POST.get("office_hours", "")
            contact_page.office_hours_ar = request.POST.get("office_hours_ar", "")

            # Map
            contact_page.map_embed_code = request.POST.get("map_embed_code", "")

            contact_page.save()

            messages.success(request, _("تم تحديث صفحة اتصل بنا بنجاح"))
            return redirect("main:admin_site_content")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "contact_page": contact_page,
    }

    return render(request, "admin_dashboard/edit_contactpage.html", context)


@login_required
@user_passes_test(is_admin)
def admin_edit_aboutpage(request):
    """Edit about page"""
    from content.forms import AboutPageForm

    about_page = AboutPage.get_solo()

    if request.method == "POST":
        form = AboutPageForm(request.POST, request.FILES, instance=about_page)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _("تم تحديث صفحة من نحن بنجاح"))
                return redirect("main:admin_site_content")
            except Exception as e:
                messages.error(request, f"حدث خطأ: {str(e)}")
        else:
            messages.error(request, _("يرجى تصحيح الأخطاء في النموذج"))
    else:
        form = AboutPageForm(instance=about_page)

    context = {
        "about_page": about_page,
        "form": form,
        "page_title": _("تعديل صفحة من نحن"),
    }

    return render(request, "admin_dashboard/edit_aboutpage.html", context)


@login_required
@user_passes_test(is_admin)
def admin_edit_homepage(request):
    """Edit home page"""
    home_page = HomePage.get_solo()

    if request.method == "POST":
        try:
            # Hero section
            home_page.hero_title = request.POST.get("hero_title", "")
            home_page.hero_title_ar = request.POST.get("hero_title_ar", "")
            home_page.hero_subtitle = request.POST.get("hero_subtitle", "")
            home_page.hero_subtitle_ar = request.POST.get("hero_subtitle_ar", "")
            home_page.hero_button_text = request.POST.get("hero_button_text", "")
            home_page.hero_button_text_ar = request.POST.get("hero_button_text_ar", "")
            home_page.hero_button_url = request.POST.get("hero_button_url", "")

            if "hero_image" in request.FILES:
                home_page.hero_image = request.FILES["hero_image"]

            # Statistics section
            home_page.show_statistics = request.POST.get("show_statistics") == "on"
            
            # Statistic 1
            home_page.stat1_value = int(request.POST.get("stat1_value", 15))
            home_page.stat1_title = request.POST.get("stat1_title", "")
            home_page.stat1_title_ar = request.POST.get("stat1_title_ar", "")
            home_page.stat1_subtitle = request.POST.get("stat1_subtitle", "")
            home_page.stat1_subtitle_ar = request.POST.get("stat1_subtitle_ar", "")
            home_page.stat1_icon = request.POST.get("stat1_icon", "fas fa-user-friends")
            
            # Statistic 2
            home_page.stat2_value = int(request.POST.get("stat2_value", 150))
            home_page.stat2_title = request.POST.get("stat2_title", "")
            home_page.stat2_title_ar = request.POST.get("stat2_title_ar", "")
            home_page.stat2_subtitle = request.POST.get("stat2_subtitle", "")
            home_page.stat2_subtitle_ar = request.POST.get("stat2_subtitle_ar", "")
            home_page.stat2_icon = request.POST.get("stat2_icon", "fas fa-bullhorn")
            
            # Statistic 3
            home_page.stat3_value = int(request.POST.get("stat3_value", 500))
            home_page.stat3_title = request.POST.get("stat3_title", "")
            home_page.stat3_title_ar = request.POST.get("stat3_title_ar", "")
            home_page.stat3_subtitle = request.POST.get("stat3_subtitle", "")
            home_page.stat3_subtitle_ar = request.POST.get("stat3_subtitle_ar", "")
            home_page.stat3_icon = request.POST.get("stat3_icon", "fas fa-chart-line")
            
            # Statistic 4
            home_page.stat4_value = int(request.POST.get("stat4_value", 250))
            home_page.stat4_title = request.POST.get("stat4_title", "")
            home_page.stat4_title_ar = request.POST.get("stat4_title_ar", "")
            home_page.stat4_subtitle = request.POST.get("stat4_subtitle", "")
            home_page.stat4_subtitle_ar = request.POST.get("stat4_subtitle_ar", "")
            home_page.stat4_icon = request.POST.get("stat4_icon", "fas fa-th-large")

            # Featured sections
            home_page.show_featured_categories = request.POST.get("show_featured_categories") == "on"
            home_page.show_featured_ads = request.POST.get("show_featured_ads") == "on"

            home_page.save()

            messages.success(request, _("تم تحديث الصفحة الرئيسية بنجاح"))
            return redirect("main:admin_site_content")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "home_page": home_page,
    }

    return render(request, "admin_dashboard/edit_homepage.html", context)


@login_required
@user_passes_test(is_admin)
def admin_edit_siteconfig(request):
    """Edit site configuration with all fields"""
    site_config = SiteConfiguration.get_solo()

    if request.method == "POST":
        try:
            # SEO Fields
            site_config.meta_keywords = request.POST.get("meta_keywords", "")
            site_config.meta_keywords_ar = request.POST.get("meta_keywords_ar", "")

            # Footer Content
            site_config.footer_text = request.POST.get("footer_text", "")
            site_config.footer_text_ar = request.POST.get("footer_text_ar", "")
            site_config.copyright_text = request.POST.get("copyright_text", "")

            # Verification Settings
            site_config.require_email_verification = (
                request.POST.get("require_email_verification") == "on"
            )
            site_config.require_phone_verification = (
                request.POST.get("require_phone_verification") == "on"
            )
            site_config.require_verification_for_services = (
                request.POST.get("require_verification_for_services") == "on"
            )
            site_config.verification_services_message = request.POST.get(
                "verification_services_message", ""
            )
            site_config.verification_services_message_ar = request.POST.get(
                "verification_services_message_ar", ""
            )

            # Payment Settings
            site_config.allow_online_payment = (
                request.POST.get("allow_online_payment") == "on"
            )
            site_config.allow_offline_payment = (
                request.POST.get("allow_offline_payment") == "on"
            )

            # InstaPay Settings
            if "instapay_qr_code" in request.FILES:
                site_config.instapay_qr_code = request.FILES["instapay_qr_code"]
            site_config.instapay_phone = request.POST.get("instapay_phone", "")

            # Wallet Settings
            site_config.wallet_payment_link = request.POST.get(
                "wallet_payment_link", ""
            )
            site_config.wallet_phone = request.POST.get("wallet_phone", "")

            # Offline Payment Instructions
            site_config.offline_payment_instructions = request.POST.get(
                "offline_payment_instructions", ""
            )
            site_config.offline_payment_instructions_ar = request.POST.get(
                "offline_payment_instructions_ar", ""
            )

            site_config.save()

            messages.success(request, _("تم تحديث إعدادات الموقع بنجاح"))
            return redirect("main:admin_site_content")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "site_config": site_config,
        "active_nav": "site_content",
        "page_title": _("تعديل إعدادات الموقع"),
    }

    return render(request, "admin_dashboard/edit_siteconfig.html", context)


# ============================================
# BLOG CATEGORIES MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_blog_categories(request):
    """List all blog categories"""
    categories = BlogCategory.objects.all().order_by("order", "name")

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        categories = categories.filter(
            name__icontains=search_query
        ) | categories.filter(name_en__icontains=search_query)

    # Pagination
    paginator = Paginator(categories, 20)
    page = request.GET.get("page", 1)
    categories_page = paginator.get_page(page)

    context = {
        "categories": categories_page,
        "total_categories": categories.count(),
        "active_categories": categories.filter(is_active=True).count(),
        "search_query": search_query,
    }

    return render(request, "admin_dashboard/blogs/categories_list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_blog_category_create(request):
    """Create new blog category"""
    if request.method == "POST":
        try:
            category = BlogCategory.objects.create(
                name=request.POST.get("name"),
                name_en=request.POST.get("name_en", ""),
                slug=request.POST.get("slug"),
                description=request.POST.get("description", ""),
                description_en=request.POST.get("description_en", ""),
                icon=request.POST.get("icon", "fas fa-folder"),
                color=request.POST.get("color", "#6b4c7a"),
                order=int(request.POST.get("order", 0)),
                is_active=request.POST.get("is_active") == "on",
            )

            messages.success(request, _("تم إضافة الفئة بنجاح"))
            return redirect("main:admin_blog_categories")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "form_title": "إضافة فئة جديدة",
        "submit_text": "إضافة",
    }

    return render(request, "admin_dashboard/blogs/category_form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_blog_category_edit(request, pk):
    """Edit blog category"""
    category = get_object_or_404(BlogCategory, pk=pk)

    if request.method == "POST":
        try:
            category.name = request.POST.get("name")
            category.name_en = request.POST.get("name_en", "")
            category.slug = request.POST.get("slug")
            category.description = request.POST.get("description", "")
            category.description_en = request.POST.get("description_en", "")
            category.icon = request.POST.get("icon", "fas fa-folder")
            category.color = request.POST.get("color", "#6b4c7a")
            category.order = int(request.POST.get("order", 0))
            category.is_active = request.POST.get("is_active") == "on"
            category.save()

            messages.success(request, _("تم تحديث الفئة بنجاح"))
            return redirect("main:admin_blog_categories")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "category": category,
        "form_title": "تعديل الفئة",
        "submit_text": "حفظ التعديلات",
    }

    return render(request, "admin_dashboard/blogs/category_form.html", context)


@login_required
@user_passes_test(is_admin)
def admin_blog_category_delete(request, pk):
    """Delete blog category"""
    category = get_object_or_404(BlogCategory, pk=pk)

    if request.method == "POST":
        category_name = category.name
        category.delete()
        messages.success(request, f"تم حذف الفئة '{category_name}' بنجاح")
        return redirect("main:admin_blog_categories")

    context = {
        "category": category,
        "blogs_count": category.get_blogs_count(),
    }

    return render(request, "admin_dashboard/blogs/category_delete.html", context)


# ============================================
# BLOG MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_blogs(request):
    """List all blogs"""
    blogs = (
        Blog.objects.select_related("author", "category")
        .all()
        .order_by("-published_date")
    )

    # Filter by category
    category_filter = request.GET.get("category")
    if category_filter:
        blogs = blogs.filter(category_id=category_filter)

    # Filter by status
    status_filter = request.GET.get("status")
    if status_filter == "published":
        blogs = blogs.filter(is_published=True)
    elif status_filter == "draft":
        blogs = blogs.filter(is_published=False)

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        blogs = blogs.filter(title__icontains=search_query)

    # Pagination
    paginator = Paginator(blogs, 20)
    page = request.GET.get("page", 1)
    blogs_page = paginator.get_page(page)

    context = {
        "blogs": blogs_page,
        "total_blogs": blogs.count(),
        "published_blogs": blogs.filter(is_published=True).count(),
        "draft_blogs": blogs.filter(is_published=False).count(),
        "categories": BlogCategory.objects.filter(is_active=True).order_by("order"),
        "selected_category": category_filter,
        "selected_status": status_filter,
        "search_query": search_query,
    }

    return render(request, "admin_dashboard/blogs/list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_blog_toggle_publish(request, pk):
    """Toggle blog publish status"""
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == "POST":
        blog.is_published = not blog.is_published
        blog.save()

        status = "نُشر" if blog.is_published else "تم إلغاء النشر"
        messages.success(request, f"تم تحديث حالة المدونة: {status}")

    return redirect("main:admin_blogs")


@login_required
@user_passes_test(is_admin)
def admin_blog_delete(request, pk):
    """Delete blog"""
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == "POST":
        blog_title = blog.title
        blog.delete()
        messages.success(request, f"تم حذف المدونة '{blog_title}' بنجاح")
        return redirect("main:admin_blogs")

    context = {
        "blog": blog,
        "comments_count": blog.comments.count(),
        "likes_count": blog.get_likes_count(),
    }

    return render(request, "admin_dashboard/blogs/delete.html", context)


# ============================================
# FAQ MANAGEMENT
# ============================================


@login_required
@user_passes_test(is_admin)
def admin_faqs(request):
    """List all FAQs"""
    from main.models import FAQ, FAQCategory

    faqs = (
        FAQ.objects.select_related("category")
        .all()
        .order_by("category__order", "order", "-is_popular")
    )

    # Filter by category if specified
    category_filter = request.GET.get("category")
    if category_filter:
        faqs = faqs.filter(category_id=category_filter)

    # Filter by status
    status_filter = request.GET.get("status")
    if status_filter == "active":
        faqs = faqs.filter(is_active=True)
    elif status_filter == "inactive":
        faqs = faqs.filter(is_active=False)
    elif status_filter == "popular":
        faqs = faqs.filter(is_popular=True)

    # Search
    search = request.GET.get("search")
    if search:
        faqs = faqs.filter(question_ar__icontains=search) | faqs.filter(
            question_en__icontains=search
        )

    # Pagination
    paginator = Paginator(faqs, 20)
    page = request.GET.get("page", 1)
    faqs_page = paginator.get_page(page)

    context = {
        "faqs": faqs_page,
        "total_faqs": faqs.count(),
        "active_faqs": FAQ.objects.filter(is_active=True).count(),
        "inactive_faqs": FAQ.objects.filter(is_active=False).count(),
        "popular_faqs": FAQ.objects.filter(is_popular=True).count(),
        "categories": FAQCategory.objects.filter(is_active=True).order_by("order"),
        "selected_category": category_filter,
        "selected_status": status_filter,
        "search_query": search,
    }

    return render(request, "admin_dashboard/faqs/list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_create(request):
    """Create new FAQ"""
    from main.models import FAQ, FAQCategory
    import logging

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        question_ar = request.POST.get("question_ar", "").strip()
        question_en = request.POST.get("question_en", "").strip()
        answer_ar = request.POST.get("answer_ar", "").strip()
        answer_en = request.POST.get("answer_en", "").strip()
        category_id = request.POST.get("category")
        order = request.POST.get("order", 0)
        is_active = request.POST.get("is_active") == "on"
        is_popular = request.POST.get("is_popular") == "on"

        logger.info(
            f"Creating FAQ - Question AR: {question_ar[:50]}, Category ID: {category_id}"
        )
        logger.info(
            f"Answer AR length: {len(answer_ar)}, Answer EN length: {len(answer_en)}"
        )

        # Validation
        if not question_ar:
            messages.error(request, _("السؤال بالعربية مطلوب"))
            context = {
                "categories": FAQCategory.objects.filter(is_active=True).order_by(
                    "order"
                ),
            }
            return render(request, "admin_dashboard/faqs/create.html", context)

        if not answer_ar:
            messages.error(request, _("الإجابة بالعربية مطلوبة"))
            context = {
                "categories": FAQCategory.objects.filter(is_active=True).order_by(
                    "order"
                ),
            }
            return render(request, "admin_dashboard/faqs/create.html", context)

        try:
            category = FAQCategory.objects.get(id=category_id)

            faq = FAQ.objects.create(
                question=question_ar,  # Required field, use AR as default
                question_ar=question_ar,
                question_en=(
                    question_en if question_en else question_ar
                ),  # Fallback to AR if EN is empty
                answer=answer_ar,  # Required field, use AR as default
                answer_ar=answer_ar,
                answer_en=(
                    answer_en if answer_en else answer_ar
                ),  # Fallback to AR if EN is empty
                category=category,
                order=int(order) if order else 0,
                is_active=is_active,
                is_popular=is_popular,
            )

            logger.info(f"FAQ created successfully with ID: {faq.id}")
            messages.success(request, _("تم إضافة السؤال بنجاح"))
            return redirect("main:admin_faqs")

        except FAQCategory.DoesNotExist:
            logger.error(f"Category with ID {category_id} not found")
            messages.error(request, _("الفئة المحددة غير موجودة"))
        except Exception as e:
            logger.error(f"Error creating FAQ: {str(e)}")
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "categories": FAQCategory.objects.filter(is_active=True).order_by("order"),
    }

    return render(request, "admin_dashboard/faqs/create.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_edit(request, faq_id):
    """Edit FAQ"""
    from main.models import FAQ, FAQCategory
    import logging

    logger = logging.getLogger(__name__)
    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "POST":
        question_ar = request.POST.get("question_ar", "").strip()
        question_en = request.POST.get("question_en", "").strip()
        answer_ar = request.POST.get("answer_ar", "").strip()
        answer_en = request.POST.get("answer_en", "").strip()

        faq.question = question_ar  # Update required field
        faq.question_ar = question_ar
        faq.question_en = question_en if question_en else question_ar
        faq.answer = answer_ar  # Update required field
        faq.answer_ar = answer_ar
        faq.answer_en = answer_en if answer_en else answer_ar

        category_id = request.POST.get("category")
        try:
            faq.category = FAQCategory.objects.get(id=category_id)
        except FAQCategory.DoesNotExist:
            logger.error(f"Category with ID {category_id} not found")
            messages.error(request, _("الفئة المحددة غير موجودة"))
            return redirect("main:admin_faq_edit", faq_id=faq_id)

        faq.order = int(request.POST.get("order", 0))
        faq.is_active = request.POST.get("is_active") == "on"
        faq.is_popular = request.POST.get("is_popular") == "on"

        try:
            faq.save()
            logger.info(f"FAQ {faq_id} updated successfully")
            messages.success(request, _("تم تحديث السؤال بنجاح"))
            return redirect("main:admin_faqs")
        except Exception as e:
            logger.error(f"Error updating FAQ {faq_id}: {str(e)}")
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "faq": faq,
        "categories": FAQCategory.objects.filter(is_active=True).order_by("order"),
    }

    return render(request, "admin_dashboard/faqs/edit.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_delete(request, faq_id):
    """Delete FAQ"""
    from main.models import FAQ

    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "POST":
        question = faq.question_ar
        faq.delete()
        messages.success(request, f"تم حذف السؤال '{question}' بنجاح")
        return redirect("main:admin_faqs")

    context = {
        "faq": faq,
        "views_count": faq.views_count,
    }

    return render(request, "admin_dashboard/faqs/delete.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_categories(request):
    """List all FAQ categories"""
    from main.models import FAQCategory

    categories = FAQCategory.objects.all().order_by("order")

    # Pagination
    paginator = Paginator(categories, 20)
    page = request.GET.get("page", 1)
    categories_page = paginator.get_page(page)

    context = {
        "categories": categories_page,
        "total_categories": categories.count(),
        "active_categories": categories.filter(is_active=True).count(),
    }

    return render(request, "admin_dashboard/faqs/categories.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_category_create(request):
    """Create new FAQ category"""
    from main.models import FAQCategory

    if request.method == "POST":
        name_ar = request.POST.get("name_ar")
        name_en = request.POST.get("name_en")
        description_ar = request.POST.get("description_ar", "")
        description_en = request.POST.get("description_en", "")
        order = request.POST.get("order", 0)
        is_active = request.POST.get("is_active") == "on"

        try:
            FAQCategory.objects.create(
                name_ar=name_ar,
                name_en=name_en,
                description_ar=description_ar,
                description_en=description_en,
                order=int(order),
                is_active=is_active,
            )
            messages.success(request, _("تم إضافة الفئة بنجاح"))
            return redirect("main:admin_faq_categories")
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    return render(request, "admin_dashboard/faqs/category_create.html")


@login_required
@user_passes_test(is_admin)
def admin_faq_category_edit(request, category_id):
    """Edit FAQ category"""
    from main.models import FAQCategory

    category = get_object_or_404(FAQCategory, id=category_id)

    if request.method == "POST":
        category.name_ar = request.POST.get("name_ar")
        category.name_en = request.POST.get("name_en")
        category.description_ar = request.POST.get("description_ar", "")
        category.description_en = request.POST.get("description_en", "")
        category.order = int(request.POST.get("order", 0))
        category.is_active = request.POST.get("is_active") == "on"

        try:
            category.save()
            messages.success(request, _("تم تحديث الفئة بنجاح"))
            return redirect("main:admin_faq_categories")
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "category": category,
        "faqs_count": category.faqs.count(),
    }

    return render(request, "admin_dashboard/faqs/category_edit.html", context)


@login_required
@user_passes_test(is_admin)
def admin_faq_category_delete(request, category_id):
    """Delete FAQ category"""
    from main.models import FAQCategory

    category = get_object_or_404(FAQCategory, id=category_id)

    if request.method == "POST":
        name = category.name_ar
        faqs_count = category.faqs.count()

        if faqs_count > 0:
            messages.error(
                request,
                f"لا يمكن حذف الفئة '{name}' لأنها تحتوي على {faqs_count} أسئلة. يرجى حذف الأسئلة أولاً أو نقلها لفئة أخرى.",
            )
            return redirect("main:admin_faq_categories")

        category.delete()
        messages.success(request, f"تم حذف الفئة '{name}' بنجاح")
        return redirect("main:admin_faq_categories")

    context = {
        "category": category,
        "faqs_count": category.faqs.count(),
    }

    return render(request, "admin_dashboard/faqs/category_delete.html", context)
