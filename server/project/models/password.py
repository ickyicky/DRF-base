from django.db import models
from django.contrib.auth.hashers import make_password

from project.models.base import BaseModel


class ChangePasswordModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    username = models.CharField(max_length=11)
    old_password = models.CharField(max_length=128)
    new_password = models.CharField(max_length=128)

    class Meta:
        managed = False


class DefaultPasswordModel(BaseModel):
    """
    Default password for new users. The latest one is always choosen.
    """

    password = models.CharField(max_length=128)

    class Meta:
        ordering = ["-created_date"]

    @classmethod
    def get_default(cls):
        """
        Return latest default password, if not present, returns None
        """
        if not cls.objects.exists():
            return None

        return cls.objects.latest("-created_date").password

    def set_password(self, password):
        """
        Sets default password, encrypts it.
        """
        self.password = make_password(password)


class ChangeDefaultPasswordModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    old_password = models.CharField(max_length=128)
    new_password = models.CharField(max_length=128)

    class Meta:
        managed = False

    @classmethod
    def get_default(cls):
        return DefaultPasswordModel.get_default()


class RestorePasswordModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    username = models.CharField(max_length=11)
    user_id = models.IntegerField()

    class Meta:
        managed = False
