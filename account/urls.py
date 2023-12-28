"""
URL mapping for accounting app
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from account import views


router = DefaultRouter(trailing_slash=False)
router.register('accounting', views.AccountingViewSet, basename='accounting')
router.register('category', views.CategoryViewSet, basename='category')
router.register('settings/month_target', views.MonthTargetViewSet, basename='month_target')
router.register('settings/save_money_target', views.SaveMoneyTargetViewSet, basename='save_money_target')


app_name = 'accounting'

urlpatterns = [
    path('', include(router.urls)),
    path('settings/month_target/<int:year>/<int:month>', views.retrieve_month_target_by_year_month, name='month-target-by-year-month'),
    path('settings/save_money_target/category/<int:category_id>', views.retrieve_save_money_target_by_category, name='save-money-target-by-category'),
]
