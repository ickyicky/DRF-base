from rest_framework import status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from project.views.base import ModelViewSet
from project.serializers.token import (
    TokenSerializer,
    TokenPairSerializer,
    TokenAccessSerializer,
    TokenRefreshSerializer,
)


class TokenViewSet(ModelViewSet):
    """
    Creates a pair of JSON Web Tokens:
    * Access Token - short-lived (5 minutes), used for regular access to resources,
    * Refresh Token - long-lived (1 day), used for regenerating the Access Token.

    If `remember_me` is set to `true` the Refresh Token's expiration date will be set based on the value
    of `REMEMBER_ME_REFRESH_TOKEN_LIFETIME` variable from settings.py file.

    Example POST request:
        ENDPOINT: http://localhost:8080/token
        HEADERS:
            Content-Type: application/vnd.api+json
        BODY:
            {
                "data": {
                    "type": "TokenModel",
                    "attributes": {
                        "username": "administrator",
                        "password": "administrator",
                        "remember_me": true
                    }
                }
            }

    Example output:

        {
            "data": {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU0MzE4OTY4MywidXNlcl9pZCI6MX0.oCI3Sgzowh8Vwo_73ytB7bprFwB4lU_RCRclXhZndcY",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzMTAzNTgzLCJ1c2VyX2lkIjoxfQ.IDExvV60TrLI0Wlj7zXEnufS2Jt6Luxb_Sd5w3NJpN4"
            }
        }

    Example authenticated request via cURL:

        curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzMTAzNTgzLCJ1c2VyX2lkIjoxfQ.IDExvV60TrLI0Wlj7zXEnufS2Jt6Luxb_Sd5w3NJpN4" http://localhost:8080/users
    """  # noqa

    allowed_methods = ["post"]
    permission_classes = ()
    authentication_classes = ()
    serializer_class = TokenSerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenPairSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshViewSet(TokenViewSet):
    """
    Creates a short-lived Access Token based on the long-lived Refresh Token.

    Example POST request:
        ENDPOINT: http://localhost:8080/token/refresh
        HEADERS:
            Content-Type: application/vnd.api+json
        BODY:
            {
                "data": {
                    "type": "TokenRefreshModel",
                    "attributes": {
                        "refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU0MzE4OTY4MywidXNlcl9pZCI6MX0.oCI3Sgzowh8Vwo_73ytB7bprFwB4lU_RCRclXhZndcY"
                    }
                }
            }

    Example output:

        {
            "data": {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzMTA0MDI4LCJ1c2VyX2lkIjoxfQ.D7aWX-FrhNC6xYGo-F8eBSw0m3K56vHwlpu9DqXBAMM"
            }
        }
    """  # noqa

    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenAccessSerializer})
    def refresh(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
