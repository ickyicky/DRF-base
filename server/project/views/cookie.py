# import the logging library
import logging
from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from drf_yasg import openapi
from project.utils import make_utc
from drf_yasg.utils import swagger_auto_schema
from project.views.base import ModelViewSet
from project.serializers.cookie import CookieSerializer

# Get an instance of a logger
log = logging.getLogger(__name__)


class CookieViewSet(ModelViewSet):
    """
    Creates a JSON Web Token (Access Token) used for regular access to resources and set it as a cookie value.

    If `remember_me` is set to `true` the cookie's expiration date will be set based on the value
    of `REMEMBER_ME_COOKIE_LIFETIME` variable from settings.py file. The Access Token's expiration date will
    be set to the same value.

    Example POST request:
        ENDPOINT: http://localhost:8080/cookie
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

        {}

    Example authenticated request via cURL:

        curl --cookie "CookieAccessToken=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQzMTAzNTgzLCJ1c2VyX2lkIjoxfQ.IDExvV60TrLI0Wlj7zXEnufS2Jt6Luxb_Sd5w3NJpN4" http://localhost:8080/users
    """  # noqa

    allowed_methods = ["post", "delete"]
    permission_classes = ()
    authentication_classes = ()
    serializer_class = CookieSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Schema(
                "Empty response body", type=openapi.TYPE_OBJECT
            )
        }
    )
    def sign_in(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(status=status.HTTP_200_OK)

        if "remember_me" in request.data and request.data["remember_me"]:
            response.set_cookie(
                key=settings.COOKIE_AUTH["COOKIE_NAME"],
                value=serializer.validated_data["token"],
                expires=make_utc(
                    datetime.utcnow()
                    + settings.COOKIE_AUTH["REMEMBER_ME_COOKIE_LIFETIME"]
                ),
                httponly=True,
            )
        else:
            response.set_cookie(
                key=settings.COOKIE_AUTH["COOKIE_NAME"],
                value=serializer.validated_data["token"],
                httponly=True,
            )

        response.data = serializer.validated_data["user"]

        return response

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Schema(
                "Empty response body", type=openapi.TYPE_OBJECT
            )
        }
    )
    def sign_out(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.COOKIE_AUTH["COOKIE_NAME"])

        return response
