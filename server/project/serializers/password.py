from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password

from project.utils import make_aware
from project.models.user import UserModel
from project.models.password import (
    ChangePasswordModel,
    RestorePasswordModel,
    ChangeDefaultPasswordModel,
)
from rest_framework_json_api import serializers
from project.serializers.base import ModelSerializer


def is_password_strong(password):
    """
    Returns a boolean indicating if the password is strong enough.

    Strong password contains at least:
    * 8 characters,
    * one uppercase letter,
    * one lowercase letter.
    """
    return (
        len(password) >= 8
        and password != password.upper()
        and password != password.lower()
        and any(c.isdigit() for c in password)
    )


class ChangePasswordSerializer(ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    old_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = ChangePasswordModel
        fields = ["old_password", "new_password"]

    def validate_old_password(self, data):

        if not check_password(data, self.context["user"].password):
            raise serializers.ValidationError("Niepoprawne dane.")

        return data

    def validate_new_password(self, data):
        if not is_password_strong(data):
            raise serializers.ValidationError(
                "Nowe hasło powinno zaiwerac minimum 8 znaków, "
                "przyajmniej jedną małą oraz dużą literę oraz "
                "liczbę."
            )

        return data


class ChangeDefaultPasswordSerializer(ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    old_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = ChangeDefaultPasswordModel
        fields = ["old_password", "new_password"]

    def validate_old_password(self, data):
        current = self.Meta.model.get_default()

        if current and not check_password(
            data, current.password
        ):
            raise serializers.ValidationError("Niepoprawne dane.")

        return data

    def validate_new_password(self, data):
        if not is_password_strong(data):
            raise serializers.ValidationError(
                "Nowe hasło powinno zaiwerac minimum 8 znaków, "
                "przyajmniej jedną małą oraz dużą literę oraz "
                "liczbę."
            )

        return data


class RestorePasswordSerializer(serializers.ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    username = serializers.CharField()

    class Meta:
        model = RestorePasswordModel
        fields = ["username"]

    def validate_username(self, data):
        if not UserModel.objects.filter(username=data).exists():
            raise serializers.ValidationError("Niepoprawna nazwa użytkownika.")

        user = UserModel.objects.filter(username=data).get()

        if (
            user.last_password_change
            and make_aware(datetime.utcnow() - timedelta(minutes=5))
            < user.last_password_change
        ):
            raise serializers.ValidationError(
                "Hasło było zmieniane w niedawnym czasie, proszę spróbować za 5 minut."
            )

        return user


class RestoreDefaultPasswordSerializer(serializers.ModelSerializer):
    """
    This class is used only to generate a proper documentation data.
    """

    user_id = serializers.IntegerField()

    class Meta:
        model = RestorePasswordModel
        fields = ["user_id"]

    def validate_user_id(self, data):
        if not UserModel.objects.filter(id=data).exists():
            raise serializers.ValidationError("Niepoprawne ID użytkownika.")

        user = UserModel.objects.filter(id=data).get()

        return user
