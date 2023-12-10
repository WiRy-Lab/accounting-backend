"""
URL mapping for user API
"""
from django.urls import path

from user import views

app_name = "auth"

urlpatterns = [
    path("register", views.CreateUserView.as_view(), name="register"),
    path("login", views.CreateTokenView.as_view(), name="login"),
    path("me", views.ManageUserView.as_view(), name="me"),
]
