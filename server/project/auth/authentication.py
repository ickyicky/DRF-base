from django.conf import settings
from django.http import HttpResponse
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from jose import jwt
from project.auth.token import AccessToken


class JWTAuthentication(BaseAuthentication):
    model = None

    def authenticate(self, request):
        self.model = get_user_model()
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != bytes(
            settings.JWT_AUTH["AUTH_HEADER_TYPES"][0].lower(), "utf-8"
        ):
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid token, invalid credentials.")
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed("Invalid token")

        return self.authenticate_credentials(auth[1])

    def authenticate_credentials(self, token):
        try:
            access_token = AccessToken(token=token)
            user_id = access_token.payload[settings.JWT_AUTH["USER_ID_CLAIM"]]

            user = self.model.objects.get(id=user_id, is_active=True)
            access_token.verify(valid_time=user.last_password_change)
        except jwt.ExpiredSignatureError or jwt.JWTError or jwt.JWTClaimsError:
            return HttpResponse({"Error": "Token is invalid"}, status="403")
        except self.model.DoesNotExist:
            return HttpResponse({"Error": "Internal server error"}, status="500")

        return (user, access_token)

    def authenticate_header(self, request):
        return settings.JWT_AUTH["AUTH_HEADER_TYPES"][0]


class CookieAuthentication(JWTAuthentication):
    model = None

    def authenticate(self, request):
        self.model = get_user_model()

        if settings.COOKIE_AUTH["COOKIE_NAME"] not in request.COOKIES:
            return None

        auth = request.COOKIES[settings.COOKIE_AUTH["COOKIE_NAME"]]

        return self.authenticate_credentials(auth)
