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
from content.models import Blog
from django.utils.translation import gettext_lazy as _
import json


def is_staff(user):
    """Check if user is staff"""
    return user.is_staff


def staff_required(view_func):
    """
    Decorator to check if user is staff.
    Returns JSON error for AJAX requests instead of redirect.
    """

    @login_required
    def wrapper(request, *args, **kwargs):
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

    context = {
        "blogs": blogs_page,
        "total_blogs": total_blogs,
        "published_blogs": published_blogs,
        "draft_blogs": draft_blogs,
        "status_filter": status_filter,
        "search_query": search_query,
        "sort_by": sort_by,
        "active_nav": "blogs",
        "page_title": _("إدارة المدونات"),
    }

    return render(request, "admin_dashboard/blogs.html", context)


@staff_required
def admin_blog_create(request):
    """
    Create new blog post via AJAX
    """
    if request.method == "POST":
        try:
            title = request.POST.get("title", "").strip()
            content = request.POST.get("content", "").strip()
            is_published = request.POST.get("is_published") == "true"
            tags = request.POST.get("tags", "").strip()
            image = request.FILES.get("image")

            # Validation
            if not title or not content:
                return JsonResponse(
                    {"success": False, "error": _("العنوان والمحتوى مطلوبان")}
                )

            # Create blog
            blog = Blog.objects.create(
                title=title,
                content=content,
                author=request.user,
                is_published=is_published,
                image=image,
            )

            # Add tags
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                blog.tags.add(*tag_list)

            return JsonResponse(
                {
                    "success": True,
                    "message": _("تم إنشاء المدونة بنجاح"),
                    "blog_id": blog.id,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": _("طريقة غير صالحة")})


@staff_required
def admin_blog_update(request, blog_id):
    """
    Update existing blog post via AJAX
    """
    try:
        blog = get_object_or_404(Blog, id=blog_id)
    except Blog.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "error": _("المدونة غير موجودة")}, status=404
            )
        return HttpResponseNotFound(_("المدونة غير موجودة"))

    if request.method == "POST":
        try:
            title = request.POST.get("title", "").strip()
            content = request.POST.get("content", "").strip()
            is_published = request.POST.get("is_published") == "true"
            tags = request.POST.get("tags", "").strip()
            image = request.FILES.get("image")

            # Validation
            if not title or not content:
                return JsonResponse(
                    {"success": False, "error": _("العنوان والمحتوى مطلوبان")}
                )

            # Update blog
            blog.title = title
            blog.content = content
            blog.is_published = is_published

            if image:
                blog.image = image

            blog.save()

            # Update tags
            blog.tags.clear()
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                blog.tags.add(*tag_list)

            return JsonResponse(
                {"success": True, "message": _("تم تحديث المدونة بنجاح")}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - return blog data
    tags_str = ", ".join([tag.name for tag in blog.tags.all()])

    return JsonResponse(
        {
            "success": True,
            "blog": {
                "id": blog.id,
                "title": blog.title,
                "content": blog.content,
                "is_published": blog.is_published,
                "tags": tags_str,
                "image_url": blog.image.url if blog.image else None,
            },
        }
    )


@staff_required
def admin_blog_delete(request, blog_id):
    """
    Delete blog post via AJAX
    """
    if request.method == "POST":
        blog = get_object_or_404(Blog, id=blog_id)
        blog_title = blog.title

        try:
            blog.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": _('تم حذف المدونة "{}" بنجاح').format(blog_title),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": _("طريقة غير صالحة")})


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
