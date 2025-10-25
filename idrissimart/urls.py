from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", include("main.api.api_url")),
    path("rosetta/", include("rosetta.urls")),  # Add Rosetta
]

urlpatterns += i18n_patterns(
    path("", include("main.urls", namespace="main")),  # Your main app
    path("admin/", admin.site.urls),
    path("content/", include("content.urls", namespace="content")),  # Your content app
)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
