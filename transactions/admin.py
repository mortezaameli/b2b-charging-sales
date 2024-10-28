from django.contrib import admin
from transactions.models import Transaction


@admin.register(Transaction)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['seller', 'transaction_type', 'amount', 'balance_request']
