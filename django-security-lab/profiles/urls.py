"""profiles/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("view/",         views.profile_view, name="profile_view"),
    path("view/<int:user_id>/", views.profile_view, name="profile_view_id"),
    path("edit/",         views.profile_edit, name="profile_edit"),
]
