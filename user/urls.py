from django.urls import path

from .views import ListUser, CreateUser

urlpatterns = [
    path("", CreateUser.as_view()),
    path("<int:user_id>", ListUser.as_view()),
]
