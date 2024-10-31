from rest_framework.permissions import BasePermission
from django.conf import settings


class SpecialTestingTokenPermission(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        return auth_header == settings.TESTING_API_TOKEN
