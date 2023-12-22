"""
URL mapping for charts app
"""
from django.urls import path

from charts import views

app_name = "charts"

urlpatterns = [
    path("range_cost", views.ChartsAPIView.as_view(), name="range_cost"),
]
