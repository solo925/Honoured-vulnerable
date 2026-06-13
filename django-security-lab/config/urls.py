"""config/urls.py"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Expose the dashboard home at the site root
from dashboard import views as dashboard_views

urlpatterns = [
    path("", dashboard_views.dashboard_home, name="home"),
    path("admin/",    admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("feedback/", include("feedback.urls")),
    path("documents/",include("documents.urls")),
    path("dashboard/",include("dashboard.urls")),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
