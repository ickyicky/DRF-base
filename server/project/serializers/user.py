from project.models.user import UserModel
from rest_framework_json_api import serializers
from project.serializers.base import PartialUpdateModelSerializer
from project.serializers.password import is_password_strong


class UserModelSerializer(PartialUpdateModelSerializer):
    """
    Get user information such as last activity, first and last name etc.
    """

    username = serializers.CharField(read_only=True, help_text="User's username.")
    first_name = serializers.CharField(read_only=False, help_text="Given name.")
    last_name = serializers.CharField(read_only=False, help_text="Family name.")
    last_password_change = serializers.DateTimeField(
        read_only=True,
        help_text="Date and time when user changed the password for the last time.",
    )
    last_activity = serializers.DateTimeField(
        read_only=True, help_text="Date of users last activity."
    )

    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "last_password_change",
            "role",
            "last_activity",
        )


class CreateUserModelSerializer(PartialUpdateModelSerializer):
    """
    Creates new user.
    """

    username = serializers.CharField(
        read_only=False, required=True, help_text="User's username."
    )
    first_name = serializers.CharField(
        read_only=False, required=True, help_text="Given name."
    )
    last_name = serializers.CharField(
        read_only=False, required=True, help_text="Family name."
    )
    password = serializers.CharField(
        read_only=False, required=False, help_text="Password."
    )

    class Meta:
        model = UserModel
        fields = ("username", "first_name", "last_name", "password")

    def validate_password(self, data):
        if not is_password_strong(data):
            raise serializers.ValidationError("Password too weak.")

        return data
