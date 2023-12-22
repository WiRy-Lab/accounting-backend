"""
URL mapping for charts app
"""
from django.urls import path

from dev import views

app_name = "dev"

urlpatterns = [
    path("generate_accounting", views.GenerateAccountingRecordsView.as_view(), name="generate_accounting"),
]
