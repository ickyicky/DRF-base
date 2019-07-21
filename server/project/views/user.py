from rest_framework.permissions import IsAuthenticated
from project.permissions.permissions import IsAdministratorOrReadOnly

from project.views.base import ModelViewSet
from project.models.user import Role, UserModel
from project.filters.user import UserModelFilter
from project.serializers.user import UserModelSerializer, CreateUserModelSerializer


class UserViewSet(ModelViewSet):
    """
    UserModel viewset, allows to create user, update it's data and also create
    new ones.
    """

    http_method_names = ["get", "patch", "post"]
    search_fields = ["first_name", "last_name", "id", "driver_id", "username"]
    queryset = UserModel.objects.all()

    serializer_class = UserModelSerializer
    serializer_classes = {"create": CreateUserModelSerializer}
    permission_classes = (IsAuthenticated, IsAdministratorOrReadOnly)
    filter_class = UserModelFilter

    def get_queryset(self):
        """
        Makes sure, that only administrator can view different users data.
        """
        user = self.request.user

        if user.role == Role.ADMINISTRATOR.name:
            return self.queryset

        return UserModel.objects.filter(id=user.id)
