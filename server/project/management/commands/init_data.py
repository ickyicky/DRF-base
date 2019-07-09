from django.core.management import BaseCommand

from project.models.user import Role, UserModel
from project.models.password import DefaultPasswordModel


class Command(BaseCommand):
    help = "Load example data"

    def handle(self, *args, **options):

        # Create user for each available Role
        administrator = UserModel(
            username="administrator", role=Role.ADMINISTRATOR.name
        )
        administrator.set_password("AdMiNi!2#")
        administrator.save()

        default_password = DefaultPasswordModel()
        default_password.set_password("123Haslo")
        default_password.save()
