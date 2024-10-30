from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Seller


class SellerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Seller
        fields = ('username', 'password')

    def create(self, validated_data):
        # Create the User
        user = User.objects.create_user(
            username=validated_data['username'], password=validated_data['password']
        )

        # Create the Seller
        seller = Seller.objects.create(user=user)
        return seller
