from six import text_type
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from jose import jwt
from project.tasks import mail
from drf_yasg.utils import swagger_auto_schema
from project.auth.token import InvalidToken, PassResetToken
from project.views.base import ModelViewSet
from project.models.user import UserModel
from project.models.password import DefaultPasswordModel
from project.serializers.password import (
    ChangePasswordSerializer,
    RestorePasswordSerializer,
    ChangeDefaultPasswordSerializer,
    RestoreDefaultPasswordSerializer,
)
from project.permissions.permissions import IsAdministrator


class ChangePasswordViewSet(ModelViewSet):
    """Change password

    Change password for a currently signed in user.
    """

    http_method_names = ["post"]
    queryset = UserModel.objects.all()

    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=["post"], detail=False)
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "Password changed correctly.",
            status.HTTP_400_BAD_REQUEST: "Incorrect data provided.",
        }
    )
    def change_password(self, request, *args, **kwargs):
        authenticated_user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        authenticated_user.set_password(serializer.validated_data["new_password"])

        return Response(status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {"user": self.request.user}


class ChangeDefaultPasswordViewSet(ModelViewSet):
    """Change default password

    Change default password for imported or created users.
    """

    http_method_names = ["post"]
    queryset = DefaultPasswordModel.objects.all().order_by("-created_date")

    serializer_class = ChangeDefaultPasswordSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)

    @action(methods=["post"], detail=False)
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "Password changed correctly.",
            status.HTTP_400_BAD_REQUEST: "Incorrect data provided.",
        }
    )
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pas = DefaultPasswordModel()
        pas.set_password(serializer.validated_data["new_password"])
        pas.save()

        return Response(status=status.HTTP_200_OK)

    def get_serializer_context(self):
        if not self.queryset.exists():
            return {"current": None}
        return {"current": self.queryset.filter()[:1].get()}


class RestorePasswordViewSet(ModelViewSet):
    """Restore password

    Allows to send a request to the Administrator to restore the password.
    """

    http_method_names = ["post"]
    queryset = UserModel.objects.all()

    serializer_class = RestorePasswordSerializer
    permission_classes = ()

    @action(methods=["post"], detail=False)
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "Request successfully sent to the Administrator.",
            status.HTTP_400_BAD_REQUEST: "Invalid username or password recentry restored.",
        }
    )
    def restore_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["username"]
        token = PassResetToken.get_token_for_user(user)
        kwargs = {
            "recipients": [],
            "subject": "Example subject",
            "message": text_type(token.encode()),
        }

        mail.apply_async(kwargs=kwargs)

        return Response(status=status.HTTP_200_OK)


class RestoreDefaultPasswordViewSet(ModelViewSet):
    """Restore password

    Allows to send a request to the Administrator to restore the password.
    """

    http_method_names = ["post"]
    queryset = UserModel.objects.all()

    serializer_class = RestoreDefaultPasswordSerializer
    permission_classes = (IsAuthenticated, IsAdministrator)

    @action(methods=["post"], detail=False)
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "Request successfully sent to the Administrator.",
            status.HTTP_400_BAD_REQUEST: "Invalid username or password recentry restored.",
        }
    )
    def restore_password(self, request, user_id, *args, **kwargs):
        serializer = self.get_serializer(data={"user_id": user_id})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user_id"]
        user.restore_default_password()

        return Response(status=status.HTTP_200_OK)


class ResetPasswordViewSet(View):
    permission_classes = ()
    serializer_class = None
    http_method_names = ["get"]

    def get(self, request, token):
        try:
            token = PassResetToken(token=token)
            user_id = token.payload[settings.JWT_AUTH["USER_ID_CLAIM"]]

            user = UserModel.objects.get(id=user_id)

            token.verify(valid_time=user.last_password_change)
        except (
            jwt.ExpiredSignatureError,
            jwt.JWTError,
            jwt.JWTClaimsError,
            UserModel.DoesNotExist,
            InvalidToken,
        ):
            return JsonResponse({"Error": "Token is invalid"}, status="403")

        user.restore_default_password()

        return JsonResponse({"Message": "Password changed"}, status="200")
