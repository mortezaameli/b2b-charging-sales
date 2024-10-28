from rest_framework import serializers
from .models import BalanceRequest, RechargeRequest


class BalanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceRequest
        fields = ['amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']


class RechargeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeRequest
        fields = ['id', 'seller', 'phone_number', 'amount', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at', 'seller']
