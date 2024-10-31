from django.contrib import admin
from billing.models import BalanceRequest, Transaction


@admin.register(BalanceRequest)
class BalanceRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'amount', 'status']

@admin.register(Transaction)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'transaction_type', 'amount', 'balance_request']
