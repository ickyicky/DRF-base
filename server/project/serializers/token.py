from django.conf import settings
from django.http import HttpResponse
from django.utils.six import text_type
from django.contrib.auth import authenticate

from jose import jwt
from project.auth.token import RefreshToken
from project.models.user import UserModel
from project.models.token import (
    TokenModel,
    TokenPairModel,
    TokenAccessModel,
    TokenRefreshModel,
)
from rest_framework_json_api import serializers


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(help_text="Personal Identity Number (PESEL)")
    password = serializers.CharField()
    remember_me = serializers.BooleanField(
        required=False,
        help_text="""If this attribute has a value of True the refresh token will
        be valid for a time defined by the `REMEMBER_ME_REFRESH_TOKEN_LIFETIME`
        settings variable (30 days by default).
        """,
    )

    def validate(self, attrs):
        user = authenticate(
            **{"username": attrs["username"], "password": attrs["password"]}
        )

        if not user:
            raise serializers.ValidationError(
                "Nie znaleziono aktywnego konta o podanych danych logowania."
            )

        refresh = self.get_token(user, attrs.get("remember_me", False))

        data = {
            "refresh": text_type(refresh.encode()),
            "access": text_type(refresh.access_token.encode()),
        }

        return data

    @classmethod
    def get_token(cls, user, remember_me=False):
        return RefreshToken.get_token_for_user(user, remember_me)

    class Meta:
        model = TokenModel
        fields = "__all__"


class TokenPairSerializer(serializers.ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    access_token = serializers.CharField(help_text="Token used to access resources.")
    refresh_token = serializers.CharField(
        help_text="Token used to generate a new Access Token."
    )

    class Meta:
        model = TokenPairModel
        fields = ["access_token", "refresh_token"]


class TokenAccessSerializer(serializers.ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    access_token = serializers.CharField(help_text="Token used to access resources.")

    class Meta:
        model = TokenAccessModel
        fields = ["access_token"]


class TokenRefreshSerializer(serializers.ModelSerializer):
    refresh_token = serializers.CharField(
        help_text="Token used to generate a new Access Token."
    )

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh_token"])

            user_id = refresh.payload[settings.JWT_AUTH["USER_ID_CLAIM"]]

            user = UserModel.objects.get(id=user_id, is_active=True)
            refresh.verify(valid_time=user.last_password_change)
        except (jwt.ExpiredSignatureError, jwt.JWTError, jwt.JWTClaimsError):
            return HttpResponse({"Error": "Token is invalid"}, status="403")
        except UserModel.DoesNotExist:
            return HttpResponse({"Error": "Internal server error"}, status="500")

        data = {"access": text_type(refresh.access_token.encode())}

        return data

    class Meta:
        model = TokenRefreshModel
        fields = ["refresh_token"]
