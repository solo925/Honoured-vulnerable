"""feedback/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("submit/", views.submit_feedback, name="feedback_submit"),
    path("wall/",   views.feedback_wall,   name="feedback_wall"),
    path("search/", views.feedback_search, name="feedback_search"),
]
