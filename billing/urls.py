from django.urls import path
from . import views


urlpatterns = [
    path(
        'balance-request/',
        views.BalanceRequestCreateView.as_view(),
        name='balance-request',
    ),
    path(
        'recharge-mobile/',
        views.RechargeMobileAPIView.as_view(),
        name='recharge_mobile',
    ),
]
