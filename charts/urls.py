"""
URL mapping for charts app
"""
from django.urls import path

from charts import views

app_name = "charts"

urlpatterns = [
    path("range_cost", views.ChartsAPIView.as_view(), name="range_cost"),
    path('target/<int:year>/<int:month>', views.TargetAPIView.as_view(), name='target'),
    path('type_cost', views.TypeCostAPIView.as_view(), name='type_cost'),
    path('compare_cost', views.CompareAPIView.as_view(), name='compare_cost'),
    path('save_target/<int:category_id>', views.SaveMoneyAPIView.as_view(), name='save_target'),
]
