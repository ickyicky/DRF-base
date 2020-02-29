# -*- coding:utf-8 -*-
import random
from copy import deepcopy

import pytest
from faker import Faker

from api.models.user import Role, UserModel

USERNAME_CHARSET = "0123456789"


def generate_username():
    """ Generate globally unique usernames. """
    while True:
        username = "".join([random.choice(USERNAME_CHARSET) for _ in range(11)])

        try:
            if username not in generate_username.usernames:
                generate_username.usernames.add(username)
                return username
        except AttributeError:
            generate_username.usernames = {username}
            return username


@pytest.fixture()
def user_attributes():
    return {
        "username": generate_username(),
        "password": Faker().password(length=8, digits=True, upper_case=True, lower_case=True),
        "role": Role.USER.name,
    }


@pytest.fixture()
def user_payload(user_attributes):
    return {
        "data": {
            "type": "UserModel",
            "attributes": user_attributes
        }
    }


@pytest.fixture()
def user_factory(user_attributes):
    def factory(*args, **kwargs):
        data = deepcopy(user_attributes)
        data["username"] = generate_username()

        data.update(**kwargs)
        user = UserModel.objects.create(**data)
        user.save()

        return user

    return factory


@pytest.fixture()
def administrator(user_factory):
    administrator = user_factory(
        username="Administrator",
        role=Role.ADMINISTRATOR.name
    )

    return administrator
