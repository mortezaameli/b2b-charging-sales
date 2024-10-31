from rest_framework import serializers
from .models import BalanceRequest


class BalanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceRequest
        fields = ['id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class RechargeMobileSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True, min_value=0)
    phone_number = serializers.CharField(required=True)
