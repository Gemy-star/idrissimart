from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from content.models import Country
from main.forms import ContactForm
from main.models import AboutPage, Category, ContactInfo


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's selected country from session
        selected_country = self.request.session.get('selected_country', 'SA')

        # Get categories by country and section
        categories_by_section = {}
        section_types = Category.SectionType.choices

        for section_code, section_name in section_types:
            categories = Category.get_root_categories(
                section_type=section_code,
                country_code=selected_country
            )[:6]  # Limit to 6 main categories per section

            categories_with_subcats = []
            for category in categories:
                subcategories = category.subcategories.filter(is_active=True)[:5]  # Limit subcategories
                categories_with_subcats.append({
                    'category': category,
                    'subcategories': subcategories
                })

            categories_by_section[section_code] = {
                'name': section_name,
                'categories': categories_with_subcats
            }

        # Get cart and wishlist counts from session
        cart_count = len(self.request.session.get('cart', []))
        wishlist_count = len(self.request.session.get('wishlist', []))

        context["selected_country"] = selected_country
        context["categories_by_section"] = categories_by_section
        context["cart_count"] = cart_count
        context["wishlist_count"] = wishlist_count
        context["page_title"] = _("الرئيسية - إدريسي مارت")
        context["meta_description"] = _("منصة تجمع سوق واحد للمختصصين والحرفيين والجمهور العام")

        return context


class CategoriesView(TemplateView):
    template_name = "pages/categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get active section from URL parameter
        active_section = self.request.GET.get('section', 'all')

        # Get user's selected country from session
        selected_country = self.request.session.get('selected_country', 'SA')

        # Get categories by country and section
        categories_by_section = {}
        section_types = Category.SectionType.choices

        for section_code, section_name in section_types:
            categories = Category.get_root_categories(
                section_type=section_code,
                country_code=selected_country
            )

            categories_with_subcats = []
            for category in categories:
                subcategories = category.subcategories.filter(is_active=True)
                categories_with_subcats.append({
                    'category': category,
                    'subcategories': subcategories
                })

            categories_by_section[section_code] = {
                'name': section_name,
                'categories': categories_with_subcats
            }

        # Get cart and wishlist counts from session
        cart_count = len(self.request.session.get('cart', []))
        wishlist_count = len(self.request.session.get('wishlist', []))

        context["selected_country"] = selected_country
        context["categories_by_section"] = categories_by_section
        context["active_section"] = active_section
        context["cart_count"] = cart_count
        context["wishlist_count"] = wishlist_count
        context["page_title"] = _("الفئات - إدريسي مارت")
        context["meta_description"] = _("استكشف جميع فئات منصة إدريسي مارت المتنوعة")

        return context


@require_POST
def set_country(request):
    """
    API endpoint to set user's selected country
    """
    try:
        country_code = request.POST.get('country_code')

        if not country_code:
            return JsonResponse({
                'success': False,
                'message': _('لم يتم تحديد البلد')
            }, status=400)

        # Validate country exists and is active
        try:
            country = Country.objects.get(code=country_code, is_active=True)
        except Country.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': _('البلد المحدد غير متاح')
            }, status=404)

        # Store in session
        request.session['selected_country'] = country_code
        request.session['selected_country_name'] = country.name

        # Optional: Store in user profile if authenticated
        if request.user.is_authenticated:
            request.user.profile.country = country
            request.user.profile.save()

        return JsonResponse({
            'success': True,
            'message': _('تم تغيير البلد بنجاح'),
            'country_code': country_code,
            'country_name': country.name
        })

    except Exception:
        return JsonResponse({
            'success': False,
            'message': _('حدث خطأ في تغيير البلد')
        }, status=500)


class CategoryDetailView(TemplateView):
    """Temporary category detail view - to be implemented later"""
    template_name = "pages/category_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        try:
            category = Category.objects.get(slug=slug, is_active=True)
            context['category'] = category
            context['subcategories'] = category.subcategories.filter(is_active=True)
        except Category.DoesNotExist:
            context['category'] = None
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get about page content
        about_content = AboutPage.get_active_content()
        if not about_content:
            # Create default content if none exists
            about_content = AboutPage.objects.create(
                title="إدريسي مارت",
                tagline="تميّزك… ملموس",
                subtitle="منصتك للتجارة الإلكترونية المتكاملة",
                who_we_are_content="""
                منصة <strong>إدريسي مارت</strong> هي منصة سعودية متخصصة في التجارة الإلكترونية المتكاملة،
                تأسست لتجمع بين البائعين المعتمدين والمشترين في سوق واحد متنوع.

                نهدف إلى تسهيل تجربة التسوق والبيع من خلال منصة موحدة تضم تنوعاً كبيراً من المنتجات والخدمات،
                وتدعم البائعين المحليين للوصول إلى جمهور أوسع.

                نعتز بانطلاقنا من قلب المملكة، لنكون المنصة التي تجمع الإبداع المحلي بروح التطور العالمي
                في عالم التجارة الإلكترونية.
                """,
                vision_content="""
                أن نكون المنصة السعودية الرائدة في التجارة الإلكترونية المتكاملة،
                التي تُلهم وتُبرز التميّز في كل قطاع وخدمة.
                """,
                mission_content="""
                نحوّل أفكار التجارة والخدمات إلى تجارب رقمية متكاملة تعبّر عن الجودة،
                وتبني أقوى الروابط بين البائعين والعملاء في المملكة.
                """
            )

        context['about_content'] = about_content
        context['page_title'] = _("من نحن - إدريسي مارت")
        context['meta_description'] = _("تعرف على منصة إدريسي مارت ورؤيتنا ورسالتنا")

        return context


class ContactView(TemplateView):
    """Contact page view with form handling"""
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get contact information
        contact_info = ContactInfo.get_active_info()
        if not contact_info:
            # Create default contact info if none exists
            contact_info = ContactInfo.objects.create(
                phone="+966 11 123 4567",
                email="info@idrissimart.com",
                address="الرياض، المملكة العربية السعودية",
                whatsapp="+966 50 123 4567",
                map_embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3620.059022564443!2d46.71516947512605!3d24.7038092779999!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3e2f05072c84c457%3A0xf45cf328d8856bac!2z2KfZhNi52YbYqSDYp9mE2KfYsdiz2YrYp9mEINin2YTYrNix2KfYtNmK2Kkg2YTZhNmF2YrYp9ix2KfYqiDYp9mE2YXYrdmK2KfYqiDYp9mE2KfZhNiz2KfZhdi52Kkg!5e0!3m2!1sar!2ssa!4v1728780637482!5m2!1sar!2ssa"
            )

        # Initialize contact form
        form = ContactForm(user=self.request.user if self.request.user.is_authenticated else None)

        context['contact_info'] = contact_info
        context['form'] = form
        context['page_title'] = _("اتصل بنا - إدريسي مارت")
        context['meta_description'] = _("تواصل معنا في إدريسي مارت")

        return context

    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        form = ContactForm(
            request.POST,
            user=request.user if request.user.is_authenticated else None
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                _("تم إرسال رسالتك بنجاح. سنتواصل معك في أقرب وقت ممكن.")
            )
            return redirect('main:contact')
        else:
            # If form is invalid, return the same page with errors
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)




@require_POST
def add_to_cart(request):
    """Add item to cart"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': _('Item ID required')}, status=400)

    cart = request.session.get('cart', [])

    if item_id not in cart:
        cart.append(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item added to cart'),
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item already in cart')
    })


@require_POST
def add_to_wishlist(request):
    """Add item to wishlist"""
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'success': False, 'message': _('Item ID required')}, status=400)

    wishlist = request.session.get('wishlist', [])

    if item_id not in wishlist:
        wishlist.append(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item added to wishlist'),
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item already in wishlist')
    })


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    item_id = request.POST.get('item_id')
    cart = request.session.get('cart', [])

    if item_id in cart:
        cart.remove(item_id)
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item removed from cart'),
            'cart_count': len(cart)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item not in cart')
    })


@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist"""
    item_id = request.POST.get('item_id')
    wishlist = request.session.get('wishlist', [])

    if item_id in wishlist:
        wishlist.remove(item_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': _('Item removed from wishlist'),
            'wishlist_count': len(wishlist)
        })

    return JsonResponse({
        'success': False,
        'message': _('Item not in wishlist')
    })
