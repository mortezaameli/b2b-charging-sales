from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import SellerSerializer


class CreateSellerView(generics.CreateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Seller created successfully."}, status=status.HTTP_201_CREATED
        )
