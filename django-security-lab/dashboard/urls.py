"""dashboard/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("",              views.dashboard_home,      name="dashboard"),
    path("url-preview/",  views.url_preview,         name="url_preview"),
    path("ping/",         views.ping_host,           name="ping"),
    path("xml-import/",   views.xml_import,          name="xml_import"),
    path("deserialize/",  views.deserialize_session, name="deserialize"),
    path("debug/",        views.debug_info,          name="debug_info"),
]
