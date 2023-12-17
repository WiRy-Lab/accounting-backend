"""
URL mapping for accounting app
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from account import views


router = DefaultRouter()
router.register('', views.AccountingViewSet, basename='accounting')

app_name = 'accounting'

urlpatterns = [
    path('', include(router.urls))
]
