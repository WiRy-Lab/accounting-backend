"""
URL mapping for accounting app
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from account import views


router = DefaultRouter(trailing_slash=False)
router.register('accounting', views.AccountingViewSet, basename='accounting')
router.register('category', views.CategoryViewSet, basename='category')

app_name = 'accounting'

urlpatterns = [
    path('', include(router.urls))
]
