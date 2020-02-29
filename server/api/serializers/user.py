from rest_framework.serializers import ModelSerializer
from api.models.user import UserModel


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "last_login",
            "first_name",
            "last_name",
            "email",
            "created_date",
            "modified_date",
            "role",
        )
