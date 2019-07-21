import json

import pytest
from faker import Faker


@pytest.mark.parametrize(
    "new_password,invalid_old,response_on_change,response_on_login",
    [
        (Faker().password(length=8, digits=True, upper_case=True), False, 200, 200),
        (Faker().password(length=8, digits=True, upper_case=True), True, 400, 400),
        (Faker().password(length=8, digits=True, upper_case=False), False, 400, 400),
    ],
)
@pytest.mark.django_db
def test_password_change(
    client,
    user_factory,
    new_password,
    invalid_old,
    response_on_change,
    response_on_login,
):
    password = Faker().password(length=8, digits=True, upper_case=True)
    u = user_factory()
    u.set_password(password, silent=True)
    u.save()
    if invalid_old:
        password = new_password

    client.force_authenticate(user=u)

    payload = {
        "data": {
            "type": "ChangePasswordModel",
            "attributes": {"old_password": password, "new_password": new_password},
        }
    }

    response = client.post(
        "/users/me/change_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == response_on_change

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": new_password},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == response_on_login


@pytest.mark.django_db
def test_default_password(client, user_factory, administrator):
    password = Faker().password(length=8, digits=True, upper_case=True)
    client.force_authenticate(user=administrator)

    payload = {
        "data": {
            "type": "ChangeDefaultPasswordModel",
            "attributes": {"old_password": password, "new_password": password},
        }
    }

    response = client.post(
        "/users/default/change_default_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 200

    u = user_factory()

    response = client.post(
        f"/users/default/{u.id}/restore_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 200

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "new_password, invalid_old, response_code",
    [
        (Faker().password(length=8, digits=True, upper_case=True), False, 200),
        (Faker().password(length=8, digits=True, upper_case=True), True, 400),
        (Faker().password(length=8, digits=True, upper_case=False), False, 400),
    ],
)
@pytest.mark.django_db
def test_change_default_password(
    client, administrator, new_password, invalid_old, response_code
):
    password = Faker().password(length=8, digits=True, upper_case=True)
    client.force_authenticate(user=administrator)
    payload = {
        "data": {
            "type": "ChangeDefaultPasswordModel",
            "attributes": {"old_password": password, "new_password": password},
        }
    }

    response = client.post(
        "/users/default/change_default_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 200

    if invalid_old:
        payload["data"]["attributes"]["old_password"] = new_password
    payload["data"]["attributes"]["new_password"] = new_password

    response = client.post(
        "/users/default/change_default_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == response_code


@pytest.mark.parametrize("invalid_username,response_code", [(False, 200), (True, 400)])
@pytest.mark.django_db
def test_restore_password(client, user_factory, invalid_username, response_code):
    u = user_factory()
    client.force_authenticate(user=u)

    username = u.username
    if invalid_username:
        username += "123"

    payload = {
        "data": {"type": "RestorePasswordModel", "attributes": {"username": username}}
    }

    response = client.post(
        "/users/me/restore_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == response_code


@pytest.mark.django_db
def test_restore_password_too_often(client, user_factory):
    u = user_factory()
    client.force_authenticate(user=u)
    username = u.username
    password = Faker().password(length=8, digits=True, upper_case=True)
    u.set_password(password)
    u.save()

    payload = {
        "data": {"type": "RestorePasswordModel", "attributes": {"username": username}}
    }

    response = client.post(
        "/users/me/restore_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_reset_password(
    client, user_factory, default_password_factory, reset_password_token_factory
):
    password = Faker().password(length=8, digits=True, upper_case=True)
    dp = default_password_factory()
    dp.set_password(password)
    dp.save()
    u = user_factory()
    token = reset_password_token_factory(user=u)

    response = client.get(
        f"/reset_password/{token}/", content_type="application/vnd.api+json"
    )

    assert response.status_code == 200

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_invalid_reset_password(client, user_factory):
    u = user_factory()

    response = client.get(
        "/reset_password/asd/", content_type="application/vnd.api+json"
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "valid,response_on_change,response_on_login", [(True, 200, 200), (False, 400, 400)]
)
@pytest.mark.django_db
def test_restore_default_password(
    client,
    administrator,
    user_factory,
    default_password_factory,
    reset_password_token_factory,
    valid,
    response_on_change,
    response_on_login,
):
    client.force_authenticate(user=administrator)
    password = Faker().password(length=8, digits=True, upper_case=True)
    dp = default_password_factory()
    dp.set_password(password)
    dp.save()
    u = user_factory()
    id = u.id
    if not valid:
        id += 1

    response = client.post(
        f"/users/default/{id}/restore_password",
        content_type="application/vnd.api+json",
    )

    assert response.status_code == response_on_change

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == response_on_login
