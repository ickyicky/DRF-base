from re import match

from django.utils.six import text_type
from django.contrib.auth import authenticate

from project.auth.token import AccessToken
from project.models.token import TokenModel
from rest_framework_json_api import serializers
from project.serializers.user import UserModelSerializer


class CookieSerializer(serializers.ModelSerializer):
    username = serializers.CharField(help_text="Personal Identity Number (PESEL)")
    password = serializers.CharField()
    remember_me = serializers.BooleanField(
        required=False,
        help_text="""If this attribute has a value of True the access token and the cookie
        will be valid for a time defined by the `REMEMBER_ME_COOKIE_LIFETIME`
        settings variable (30 days by default).
        """,
    )

    def validate(self, attrs):
        user = None

        forbidden = r"[A-Za-z0-9\.]+@[A-Za-z0-9]+\.[A-Za-z0-9]+"

        if match(forbidden, attrs["username"]):
            raise serializers.ValidationError(
                "Logowanie do panelu jest tylko po loginie z ActiveDirectory"
            )

        user = authenticate(
            **{"username": attrs["username"], "password": attrs["password"]}
        )

        if user is None or not user.is_active:
            raise serializers.ValidationError("Invalid credentials.")

        token = self.get_token(user, attrs.get("remember_me", False))

        data = {
            "token": text_type(token.encode()),
            "user": UserModelSerializer(user).data,
        }

        return data

    @classmethod
    def get_token(cls, user, remember_me=False):
        return AccessToken.get_token_for_user(user, remember_me)

    class Meta:
        model = TokenModel
        fields = "__all__"
