from rest_framework.permissions import IsAuthenticated

from project.views.base import ModelViewSet
from project.models.user import Role, UserModel
from project.filters.user import UserModelFilter
from project.serializers.user import UserModelSerializer


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "post"]
    search_fields = ["first_name", "last_name", "id", "driver_id", "username"]
    queryset = UserModel.objects.all()

    serializer_class = UserModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = UserModelFilter

    def get_queryset(self):
        user = self.request.user

        if user.role == Role.ADMINISTRATOR.name:
            return self.queryset

        return UserModel.objects.filter(id=user.id)
