from django.urls import path
from . import views


urlpatterns = [
    path('recharge/', views.RechargeCreateView.as_view(), name='create_recharge'),
    path(
        'recharge/<int:id>/', views.RechargeDetailView.as_view(), name='recharge_status'
    ),
    path('recharges/', views.RechargeListView.as_view(), name='recharge_list'),
]
