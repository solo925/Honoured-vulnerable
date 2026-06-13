"""accounts/urls.py"""

from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.login_view,name="login"),
    path("logout/",views.logout_view,name="logout"),
    path("register/",views.register_view,name="register"),
    path("reset/",views.password_reset_view,name="password_reset"),
    path("reset/<str:token>/",views.password_reset_confirm_view, name="password_reset_confirm"),
]
