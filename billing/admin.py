from django.contrib import admin
from billing.models import BalanceRequest


@admin.register(BalanceRequest)
class BalanceRequestAdmin(admin.ModelAdmin):
    list_display = ['seller', 'amount', 'status']
