from django.db import models


class TokenModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    username = models.CharField(
        max_length=11, unique=True, help_text="Personal Identity Number (PESEL)"
    )
    password = models.CharField(max_length=128)
    remember_me = models.BooleanField(
        help_text="""If this attribute has a value of True the refresh token will
        be valid for a time defined by the `REMEMBER_ME_REFRESH_TOKEN_LIFETIME`
        settings variable (30 days by default).
        """
    )

    class Meta:
        managed = False


class TokenPairModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    access_token = models.TextField(help_text="Token used to access resources.")
    refresh_token = models.TextField(
        help_text="Token used to generate a new Access Token."
    )

    class Meta:
        managed = False


class TokenAccessModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    access_token = models.TextField(help_text="Token used to access resources.")

    class Meta:
        managed = False


class TokenRefreshModel(models.Model):
    """
    This class is used only to generate a proper documentation data.
    """

    refresh_token = models.TextField(
        help_text="Token used to generate a new Access Token."
    )

    class Meta:
        managed = False
