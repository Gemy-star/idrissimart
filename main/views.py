from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "الرئيسية - إدريسي مارت"
        context[
            "meta_description"
        ] = "منصة تجمع سوق واحد للمختصصين والحرفيين والجمهور العام"
        return context
