# billing/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from .models import RechargeRequest
from sellers.models import Seller
from .serializers import BalanceRequestSerializer, RechargeRequestSerializer
from django.shortcuts import get_object_or_404


class BalanceRequestCreateView(CreateAPIView):
    serializer_class = BalanceRequestSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure that only a seller can make a request
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)

# class RechargeCreateView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = RechargeRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             seller = (
#                 request.user.seller_profile
#             )  # assuming the user is linked to a seller profile
#             amount = serializer.validated_data['amount']
#             phone_number = serializer.validated_data['phone_number']

#             # Create and process recharge request
#             recharge_request = RechargeRequest(
#                 seller=seller, amount=amount, phone_number=phone_number
#             )
#             try:
#                 recharge_request.process_recharge()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except ValueError as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RechargeDetailView(RetrieveAPIView):
#     # permission_classes = [IsAuthenticated]
#     queryset = RechargeRequest.objects.all()
#     serializer_class = RechargeRequestSerializer
#     lookup_field = 'id'


# class RechargeListView(ListAPIView):
#     # permission_classes = [IsAuthenticated]
#     serializer_class = RechargeRequestSerializer

#     def get_queryset(self):
#         return RechargeRequest.objects.filter(
#             seller=self.request.user.seller_profile
#         ).order_by('-created_at')
