"""
URL mapping for reports app
"""
from django.urls import path

from reports import views

app_name = "reports"

urlpatterns = [
    path('get_month_reports/<int:year>/<int:month>', views.MonthlyReportAPIView.as_view(), name='get_month_reports'),
    path('get_year_reports/<int:year>', views.YearlyReportAPIView.as_view(), name='get_year_reports'),
]
