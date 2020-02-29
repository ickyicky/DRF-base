import enum

from django.contrib.auth.models import AbstractUser
from django.db import models

from api.models.base import BaseModel


class Role(enum.Enum):
    ADMINISTRATOR = "Administrator"
    USER = "User"


class UserModel(BaseModel, AbstractUser):
    class JSONAPIMeta:
        resource_id = "id"

    username = models.CharField(max_length=30, unique=True, help_text="User's username.")
    role = models.CharField(
        max_length=20,
        default=Role.USER.name,
        blank=True,
        null=True,
        choices=((role.name, role.value) for role in Role),
        help_text="User's role in the system.",
    )

    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Date and time when user changed the password for the last time.",
    )

    @property
    def last_activity(self):
        if self.activity.exists():
            return self.activity.order_by("-time")[:1].get().time
        return None


class ChangePasswordModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    username = models.CharField(max_length=30)
    old_password = models.CharField(max_length=128)
    new_password = models.CharField(max_length=128)

    class Meta:
        managed = False
