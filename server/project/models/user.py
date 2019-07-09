import enum

from django.db import models
from django.contrib.auth.models import AbstractUser

from project.utils import now
from project.models.base import BaseModel
from project.models.password import DefaultPasswordModel


class Role(enum.Enum):
    ADMINISTRATOR = "Administrator"
    USER = "User"


class UserModel(BaseModel, AbstractUser):
    """
    Basic user model, with predefinied role.
    """

    class JSONAPIMeta:
        resource_id = "id"

    username = models.CharField(max_length=30, unique=True, help_text="User's ID.")
    role = models.CharField(
        max_length=20,
        null=False,
        default=Role.USER.name,
        choices=((role.name, role.value) for role in Role),
        help_text="User's role in the system.",
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Datetime when user changed the password for the last time.",
    )

    class Meta:
        ordering = ["-username"]

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = DefaultPasswordModel.get_default().password
        self.full_clean()
        return super(UserModel, self).save(*args, **kwargs)

    @property
    def last_activity(self):
        if self.activity.exists():
            return self.activity.order_by("-time")[:1].get().time
        return None

    def set_password(self, password, silent=False):
        """
        Sets password. If silent=True, last_password_change won't be set.
        """
        if self.password and not silent:
            self.last_password_change = now()

        super().set_password(password)
        self.save()

    def restore_default_password(self):
        """
        Restores default password.
        """
        default = DefaultPasswordModel.get_default()

        if default:
            self.password = default
            self.save()
