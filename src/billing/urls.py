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
    path(
        'balance-request/<int:pk>/approve/',
        views.BalanceRequestApproveView.as_view(),
        name='balance-request-approve',
    ),
    path(
        'check-db-consistency/',
        views.CheckDbConsistencyView.as_view(),
        name='check-db-consistency',
    ),
]
