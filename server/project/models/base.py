from django.db import models


class BaseModel(models.Model):
    """
    Base model, contains created and modified date.
    """

    class Meta:
        abstract = True

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
