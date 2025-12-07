"""
Views for handling ad and user reports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ClassifiedAd, User, AdReport
from .forms import AdReportForm


@login_required
@require_http_methods(["GET", "POST"])
def report_ad(request, ad_id):
    """Report an ad for inappropriate content or behavior"""
    ad = get_object_or_404(ClassifiedAd, id=ad_id)

    # Prevent users from reporting their own ads
    if ad.user == request.user:
        messages.error(request, _("لا يمكنك الإبلاغ عن إعلانك الخاص"))
        return redirect(ad.get_absolute_url())

    if request.method == "POST":
        form = AdReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_ad = ad
            # Don't validate since we set reported_ad after form validation
            report.save(validate=False)

            messages.success(
                request,
                _("تم إرسال البلاغ بنجاح. سيتم مراجعته من قبل فريق الإدارة."),
            )

            # If AJAX request, return JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": _("تم إرسال البلاغ بنجاح"),
                    }
                )

            return redirect(ad.get_absolute_url())
        else:
            # Show validation errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f"{form.fields.get(field, field).label if field in form.fields else field}: {error}",
                    )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "errors": form.errors,
                    }
                )
    else:
        form = AdReportForm()

    context = {
        "form": form,
        "ad": ad,
        "report_type": "ad",
    }

    return render(request, "report/report_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def report_user(request, user_id):
    """Report a user for inappropriate behavior"""
    reported_user = get_object_or_404(User, id=user_id)

    # Prevent users from reporting themselves
    if reported_user == request.user:
        messages.error(request, _("لا يمكنك الإبلاغ عن نفسك"))
        return redirect("home")

    if request.method == "POST":
        form = AdReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            # Don't validate since we set reported_user after form validation
            report.save(validate=False)

            messages.success(
                request,
                _("تم إرسال البلاغ بنجاح. سيتم مراجعته من قبل فريق الإدارة."),
            )

            # If AJAX request, return JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": _("تم إرسال البلاغ بنجاح"),
                    }
                )

            return redirect("home")
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "errors": form.errors,
                    }
                )
    else:
        form = AdReportForm()

    context = {
        "form": form,
        "reported_user": reported_user,
        "report_type": "user",
    }

    return render(request, "reports/report_form.html", context)


@login_required
def my_reports(request):
    """View user's submitted reports"""
    reports = AdReport.objects.filter(reporter=request.user).select_related(
        "reported_ad", "reported_user", "reviewed_by"
    )

    context = {
        "reports": reports,
    }

    return render(request, "reports/my_reports.html", context)
