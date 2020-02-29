from rest_framework_json_api.views import ModelViewSet
from api.models.user import UserModel
from rest_framework.permissions import IsAuthenticated

from api.serializers.user import UserModelSerializer
from api.permissions.permissions import IsAdministrator


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "post"]
    search_fields = ["first_name", "last_name", "id", "driver_id", "username"]
    queryset = UserModel.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)
