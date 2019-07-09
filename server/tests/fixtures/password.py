# -*- coding:utf-8 -*-
from copy import deepcopy
from six import text_type
from project.auth.token import PassResetToken

import pytest
from faker import Faker
from project.models.password import DefaultPasswordModel


@pytest.fixture()
def default_password_attributes():
    return {
        "password": Faker().password(length=8, digits=True, upper_case=True, lower_case=True),
    }


@pytest.fixture()
def default_password_payload(default_password_attributes):
    return {
        "data": {
            "type": "DefaultPasswordModel",
            "attributes": default_password_attributes
        }
    }


@pytest.fixture()
def default_password_factory(default_password_attributes):
    def factory(*args, **kwargs):
        data = deepcopy(default_password_attributes)
        data.update(**kwargs)
        default_password = DefaultPasswordModel.objects.create(**data)
        default_password.save()

        return default_password

    return factory


@pytest.fixture()
def reset_password_token_factory():
    def factory(user):
        token = PassResetToken.get_token_for_user(user)
        return text_type(token.encode())
    return factory
