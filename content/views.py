from urllib.parse import quote

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from taggit.models import Tag

from .forms import CommentForm
from .models import Blog, Comment, BlogCategory


class BlogListView(ListView):
    model = Blog
    template_name = "pages/blog_list.html"
    context_object_name = "blogs"
    paginate_by = 12  # Show 12 blogs per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_blogs"] = Blog.objects.filter(is_published=True)[:5]
        # Get all categories
        context["categories"] = BlogCategory.objects.filter(is_active=True).order_by(
            "order", "name"
        )
        # Get all tags for the "All Tags" section
        context["all_tags"] = Tag.objects.all()
        # Get top 10 most popular tags
        context["popular_tags"] = Tag.objects.annotate(
            num_posts=Count("blog")
        ).order_by("-num_posts")[:10]

        # Add current tag if filtering by tag
        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            context["current_tag"] = get_object_or_404(Tag, slug=tag_slug)

        # Add current category if filtering by category
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            context["current_category"] = get_object_or_404(
                BlogCategory, slug=category_slug
            )

        return context

    def get_queryset(self):
        queryset = (
            Blog.objects.filter(is_published=True)
            .select_related("author", "category")
            .order_by("-published_date")
        )

        # Filter by tag
        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[tag])

        # Filter by category
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            category = get_object_or_404(BlogCategory, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset


class BlogDetailView(SingleObjectMixin, FormView):
    model = Blog
    template_name = "pages/blog_detail.html"
    context_object_name = "blog"
    form_class = CommentForm
    queryset = Blog.objects.filter(is_published=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Increment views count
        self.object.increment_views()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Add related posts to the context."""
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Get IDs of tags for the current post
        tag_ids = post.tags.values_list("id", flat=True)

        # Find other posts that share tags, excluding the current post
        related_posts = Blog.objects.filter(
            tags__in=tag_ids, is_published=True
        ).exclude(id=post.id)

        # Order by the number of shared tags, then by date, and limit to 3
        context["related_posts"] = related_posts.annotate(
            same_tags=Count("tags")
        ).order_by("-same_tags", "-published_date")[:3]

        # Add social share URLs
        full_url = self.request.build_absolute_uri(post.get_absolute_url())
        context["encoded_url"] = quote(full_url)
        context["encoded_title"] = quote(post.title)
        context["full_url"] = full_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.blog = self.object
        comment.author = self.request.user
        parent_id = form.cleaned_data.get("parent_id")
        if parent_id:
            comment.parent = Comment.objects.get(id=parent_id)
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("content:blog_detail", kwargs={"slug": self.object.slug})


class BlogLikeView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            blog = get_object_or_404(Blog, slug=slug)
            user_liked = blog.likes.filter(pk=request.user.pk).exists()

            if user_liked:
                blog.likes.remove(request.user)
                liked = False
            else:
                blog.likes.add(request.user)
                liked = True

            return JsonResponse(
                {"success": True, "liked": liked, "like_count": blog.likes.count()}
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
