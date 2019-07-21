from django.conf import settings
from django.http import HttpResponse
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from jose import jwt
from project.auth.token import AccessToken


def authenticate(token_cls, token):
    """
    Authenticates user, returns user object if correct.
    """
    model = get_user_model()
    try:
        token = token_cls(token=token)
        user_id = token.payload[settings.JWT_AUTH["USER_ID_CLAIM"]]

        user = model.objects.get(id=user_id, is_active=True)
        token.verify(valid_time=user.last_password_change)
    except (
        jwt.ExpiredSignatureError,
        jwt.JWTError,
        jwt.JWTClaimsError,
        model.DoesNotExist,
    ):
        return HttpResponse({"Error": "Token is invalid"}, status="403")

    return (user, token)


class JWTAuthentication(BaseAuthentication):
    model = None

    def authenticate(self, request):
        """
        Checks if header is valid and then performs authorization.
        Returns user object if correct.
        """
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
        return authenticate(AccessToken, token)

    def authenticate_header(self, request):
        return settings.JWT_AUTH["AUTH_HEADER_TYPES"][0]


class CookieAuthentication(JWTAuthentication):
    """
    Cookie authorization requires cookie to have required cookie name,
    specified in COOKIE_AUTH settings and also use special COOKIE_NAME
    """

    model = None

    def authenticate(self, request):
        """
        Authenticates user, returns user object if correct.
        """
        self.model = get_user_model()

        if settings.COOKIE_AUTH["COOKIE_NAME"] not in request.COOKIES:
            return None

        auth = request.COOKIES[settings.COOKIE_AUTH["COOKIE_NAME"]]

        return self.authenticate_credentials(auth)
