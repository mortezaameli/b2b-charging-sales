from django.contrib import admin
from billing.models import BalanceRequest, RechargeRequest


admin.site.register(RechargeRequest)
@admin.register(BalanceRequest)
class BalanceRequestAdmin(admin.ModelAdmin):
    list_display = ['seller', 'amount', 'status']
