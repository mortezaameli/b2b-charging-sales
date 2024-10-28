from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from .services import process_recharge
from sellers.models import Seller
from .serializers import BalanceRequestSerializer, RechargeMobileSerializer
from django.shortcuts import get_object_or_404


class BalanceRequestCreateView(CreateAPIView):
    serializer_class = BalanceRequestSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure that only a seller can make a request
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)


class RechargeMobileAPIView(APIView):

    def post(self, request):
        serializer = RechargeMobileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                process_recharge(request.user, serializer.validated_data)
                return Response(
                    {"success": "Recharge processed successfully."},
                    status=status.HTTP_200_OK,
                )

            except Seller.DoesNotExist:
                return Response(
                    {"error": "Seller not found."}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
