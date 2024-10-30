from django.urls import path
from .views import CreateSellerView

urlpatterns = [
    path('create-seller/', CreateSellerView.as_view(), name='create-seller'),
]