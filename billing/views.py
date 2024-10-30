from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from . import services as BillingServices
from sellers.models import Seller
from .serializers import BalanceRequestSerializer, RechargeMobileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.forms.models import model_to_dict


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
                BillingServices.process_recharge(
                    request.user, serializer.validated_data
                )
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


class BalanceRequestApproveView(APIView):

    def patch(self, request, pk):
        try:
            BillingServices.approve_balance_request(pk)
            return Response(
                {"success": "Balance request approved successfully."},
                status=status.HTTP_200_OK,
            )

        except Http404:
            return Response(
                {"error": "Balance request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckDbConsistencyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            is_db_ok = BillingServices.check_db_consistency()
            if is_db_ok:
                return Response({"success": 'DB is OK'}, status=status.HTTP_200_OK)
            return Response(
                {"error": 'Database have consistency problem'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
