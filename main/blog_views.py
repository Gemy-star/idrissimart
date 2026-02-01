"""
Blog Management Views for Admin Dashboard
Handles CRUD operations for blog posts
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Q, Count
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.db import transaction
from content.models import Blog, BlogCategory
from django.utils.translation import gettext_lazy as _
from functools import wraps
import json

from .blog_forms import BlogForm


def is_staff(user):
    """Check if user is staff"""
    return user.is_staff


def staff_required(view_func):
    """
    Decorator to check if user is staff.
    Returns JSON error for AJAX requests instead of redirect.
    Prevents POST to GET redirect issue.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            # Check if it's an AJAX request
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("يجب تسجيل الدخول أولاً"),
                    },
                    status=401,
                )
            # Regular request - redirect to login
            return redirect("main:login")

        # Check if user is staff
        if not request.user.is_staff:
            # Check if it's an AJAX request
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "error": _("ليس لديك صلاحية للوصول إلى هذه الصفحة"),
                    },
                    status=403,
                )
            # Regular request - redirect to login or show error
            messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
            return redirect("main:home")

        return view_func(request, *args, **kwargs)

    return wrapper


@staff_required
def admin_blogs(request):
    """
    Main blog management page with list, search, and filter
    """
    # Get filter parameters
    status_filter = request.GET.get("status", "all")
    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "-published_date")

    # Base queryset
    blogs = Blog.objects.select_related("author").annotate(
        comments_count=Count("comments"), likes_count=Count("likes")
    )

    # Apply status filter
    if status_filter == "published":
        blogs = blogs.filter(is_published=True)
    elif status_filter == "draft":
        blogs = blogs.filter(is_published=False)

    # Apply search
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(author__username__icontains=search_query)
            | Q(tags__name__icontains=search_query)
        ).distinct()

    # Apply sorting
    blogs = blogs.order_by(sort_by)

    # Pagination
    paginator = Paginator(blogs, 20)
    page_number = request.GET.get("page", 1)
    blogs_page = paginator.get_page(page_number)

    # Statistics
    total_blogs = Blog.objects.count()
    published_blogs = Blog.objects.filter(is_published=True).count()
    draft_blogs = Blog.objects.filter(is_published=False).count()

    # Get categories for filters and forms
    categories = BlogCategory.objects.all()
    category_filter = request.GET.get("category", "")
    if category_filter:
        blogs = blogs.filter(category_id=category_filter)

    # Create form instance for CKEditor 5 media files
    blog_form = BlogForm()

    context = {
        "blogs": blogs_page,
        "total_blogs": total_blogs,
        "published_blogs": published_blogs,
        "draft_blogs": draft_blogs,
        "categories": categories,
        "selected_category": category_filter,
        "selected_status": status_filter if status_filter != "all" else "",
        "status_filter": status_filter,
        "search_query": search_query,
        "sort_by": sort_by,
        "blog_form": blog_form,
        "active_nav": "blogs",
        "page_title": _("إدارة المدونات"),
    }

    return render(request, "admin_dashboard/blogs_new.html", context)


@staff_required
def admin_blog_create(request):
    """
    Create new blog post
    """
    from taggit.models import Tag

    if request.method == "POST":
        try:
            with transaction.atomic():
                title = request.POST.get("title", "").strip()
                content = request.POST.get("content", "").strip()
                is_published = request.POST.get("is_published") == "on"
                allow_comments = request.POST.get("allow_comments") == "on"
                featured = request.POST.get("featured") == "on"
                tags = request.POST.get("tags", "").strip()
                image = request.FILES.get("image")
                category_id = request.POST.get("category")

                # Validation
                if not title or not content:
                    messages.error(request, _("العنوان والمحتوى مطلوبان"))
                    return redirect("main:admin_blog_create")

                # Create blog
                blog = Blog.objects.create(
                    title=title,
                    content=content,
                    author=request.user,
                    is_published=is_published,
                    allow_comments=allow_comments,
                    featured=featured if hasattr(Blog, "featured") else False,
                    image=image,
                )

                # Set category if provided
                if category_id:
                    try:
                        blog.category = BlogCategory.objects.get(id=int(category_id))
                        blog.save(update_fields=["category"])
                    except (BlogCategory.DoesNotExist, ValueError):
                        pass

                # Add tags
                if tags:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    blog.tags.add(*tag_list)

                messages.success(request, _("تم إنشاء المدونة بنجاح"))
                return redirect("main:admin_blogs")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect("main:admin_blog_create")

    # GET request - show form
    categories = BlogCategory.objects.filter(is_active=True).order_by("name")
    popular_tags = Tag.objects.all()[:10]
    form = BlogForm()

    context = {
        "form": form,
        "categories": categories,
        "popular_tags": popular_tags,
        "blog_form": form,  # For media files
        "active_nav": "blogs",
        "page_title": _("مدونة جديدة"),
    }

    return render(request, "admin_dashboard/blogs/form.html", context)


@staff_required
def admin_blog_update(request, blog_id):
    """
    Update existing blog post
    """
    from taggit.models import Tag

    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        try:
            with transaction.atomic():
                title = request.POST.get("title", "").strip()
                content = request.POST.get("content", "").strip()
                is_published = request.POST.get("is_published") == "on"
                allow_comments = request.POST.get("allow_comments") == "on"
                featured = request.POST.get("featured") == "on"
                tags = request.POST.get("tags", "").strip()
                image = request.FILES.get("image")
                remove_image = request.POST.get("remove_image") == "on"
                category_id = request.POST.get("category")

                # Validation
                if not title or not content:
                    messages.error(request, _("العنوان والمحتوى مطلوبان"))
                    return redirect("main:admin_blog_update", blog_id=blog_id)

                # Update blog
                blog.title = title
                blog.content = content
                blog.is_published = is_published
                blog.allow_comments = allow_comments
                if hasattr(Blog, "featured"):
                    blog.featured = featured

                # Handle image
                if remove_image and blog.image:
                    blog.image.delete()
                    blog.image = None
                elif image:
                    blog.image = image

                # Update category
                if category_id:
                    try:
                        blog.category = BlogCategory.objects.get(id=int(category_id))
                    except (BlogCategory.DoesNotExist, ValueError):
                        blog.category = None
                else:
                    blog.category = None

                blog.save()

                # Update tags
                blog.tags.clear()
                if tags:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    blog.tags.add(*tag_list)

                messages.success(request, _("تم تحديث المدونة بنجاح"))
                return redirect("main:admin_blogs")

        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect("main:admin_blog_update", blog_id=blog_id)

    # GET request - show form with current data
    categories = BlogCategory.objects.filter(is_active=True).order_by("name")
    popular_tags = Tag.objects.all()[:10]

    # Create form instance with blog data
    form = BlogForm(instance=blog)

    context = {
        "blog": blog,
        "form": form,
        "categories": categories,
        "popular_tags": popular_tags,
        "blog_form": form,  # For media files
        "active_nav": "blogs",
        "page_title": _("تعديل المدونة"),
    }

    return render(request, "admin_dashboard/blogs/form.html", context)


@staff_required
def admin_blog_delete(request, blog_id):
    """
    Delete blog post
    """
    blog = get_object_or_404(Blog, id=blog_id)
    blog_title = blog.title

    if request.method == "POST":
        try:
            blog.delete()

            # Check if AJAX request
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": _('تم حذف المدونة "{}" بنجاح').format(blog_title),
                    }
                )
            else:
                messages.success(
                    request, _('تم حذف المدونة "{}" بنجاح').format(blog_title)
                )
                return redirect("main:admin_blogs")

        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": str(e)})
            else:
                messages.error(request, f"حدث خطأ: {str(e)}")
                return redirect("main:admin_blogs")

    # GET request - show confirmation page
    context = {
        "blog": blog,
        "active_nav": "blogs",
    }
    return render(request, "admin_dashboard/blogs/delete.html", context)


@staff_required
def admin_blog_detail(request, blog_id):
    """
    View blog details in admin dashboard
    """
    blog = get_object_or_404(
        Blog.objects.select_related("author", "category").prefetch_related(
            "tags", "comments"
        ),
        id=blog_id,
    )

    context = {
        "blog": blog,
        "active_nav": "blogs",
    }
    return render(request, "admin_dashboard/blogs/detail.html", context)


@staff_required
def admin_blog_toggle_publish(request, blog_id):
    """
    Toggle blog publish status via AJAX
    """
    if request.method == "POST":
        blog = get_object_or_404(Blog, id=blog_id)

        try:
            blog.is_published = not blog.is_published
            blog.save()

            status_text = _("منشور") if blog.is_published else _("مسودة")

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم تغيير حالة المدونة إلى: {}").format(status_text),
                    "is_published": blog.is_published,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": _("طريقة غير صالحة")})
