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
    about_page = AboutPage.get_solo()

    if request.method == "POST":
        try:
            about_page.title = request.POST.get("title", "")
            about_page.title_ar = request.POST.get("title_ar", "")
            about_page.content = request.POST.get("content", "")
            about_page.content_ar = request.POST.get("content_ar", "")
            about_page.mission = request.POST.get("mission", "")
            about_page.mission_ar = request.POST.get("mission_ar", "")
            about_page.vision = request.POST.get("vision", "")
            about_page.vision_ar = request.POST.get("vision_ar", "")
            about_page.values = request.POST.get("values", "")
            about_page.values_ar = request.POST.get("values_ar", "")

            if "featured_image" in request.FILES:
                about_page.featured_image = request.FILES["featured_image"]

            about_page.save()

            messages.success(request, _("تم تحديث صفحة من نحن بنجاح"))
            return redirect("main:admin_site_content")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "about_page": about_page,
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

            # Modal
            home_page.show_modal = request.POST.get("show_modal") == "on"
            home_page.modal_title = request.POST.get("modal_title", "")
            home_page.modal_title_ar = request.POST.get("modal_title_ar", "")
            home_page.modal_content = request.POST.get("modal_content", "")
            home_page.modal_content_ar = request.POST.get("modal_content_ar", "")
            home_page.modal_button_text = request.POST.get("modal_button_text", "")
            home_page.modal_button_text_ar = request.POST.get(
                "modal_button_text_ar", ""
            )
            home_page.modal_button_url = request.POST.get("modal_button_url", "")

            if "modal_image" in request.FILES:
                home_page.modal_image = request.FILES["modal_image"]

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
    """Edit site configuration"""
    site_config = SiteConfiguration.get_solo()

    if request.method == "POST":
        try:
            site_config.meta_keywords = request.POST.get("meta_keywords", "")
            site_config.meta_keywords_ar = request.POST.get("meta_keywords_ar", "")
            site_config.footer_text = request.POST.get("footer_text", "")
            site_config.footer_text_ar = request.POST.get("footer_text_ar", "")
            site_config.copyright_text = request.POST.get("copyright_text", "")

            site_config.save()

            messages.success(request, _("تم تحديث إعدادات الموقع بنجاح"))
            return redirect("main:admin_site_content")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")

    context = {
        "site_config": site_config,
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

    if request.method == "POST":
        question_ar = request.POST.get("question_ar")
        question_en = request.POST.get("question_en")
        answer_ar = request.POST.get("answer_ar")
        answer_en = request.POST.get("answer_en")
        category_id = request.POST.get("category")
        order = request.POST.get("order", 0)
        is_active = request.POST.get("is_active") == "on"
        is_popular = request.POST.get("is_popular") == "on"

        try:
            category = FAQCategory.objects.get(id=category_id)

            faq = FAQ.objects.create(
                question_ar=question_ar,
                question_en=question_en,
                answer_ar=answer_ar,
                answer_en=answer_en,
                category=category,
                order=int(order),
                is_active=is_active,
                is_popular=is_popular,
            )

            messages.success(request, _("تم إضافة السؤال بنجاح"))
            return redirect("main:admin_faqs")

        except FAQCategory.DoesNotExist:
            messages.error(request, _("الفئة المحددة غير موجودة"))
        except Exception as e:
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

    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "POST":
        faq.question_ar = request.POST.get("question_ar")
        faq.question_en = request.POST.get("question_en")
        faq.answer_ar = request.POST.get("answer_ar")
        faq.answer_en = request.POST.get("answer_en")

        category_id = request.POST.get("category")
        try:
            faq.category = FAQCategory.objects.get(id=category_id)
        except FAQCategory.DoesNotExist:
            messages.error(request, _("الفئة المحددة غير موجودة"))
            return redirect("main:admin_faq_edit", faq_id=faq_id)

        faq.order = int(request.POST.get("order", 0))
        faq.is_active = request.POST.get("is_active") == "on"
        faq.is_popular = request.POST.get("is_popular") == "on"

        try:
            faq.save()
            messages.success(request, _("تم تحديث السؤال بنجاح"))
            return redirect("main:admin_faqs")
        except Exception as e:
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
