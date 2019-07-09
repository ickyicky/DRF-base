import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_password_change(client, user_factory):
    password = Faker().password(length=8, digits=True, upper_case=True)
    new_password = Faker().password(length=8, digits=True, upper_case=True)
    u = user_factory()
    u.set_password(password, silent=True)
    u.save()

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

    assert response.status_code == 200

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": new_password},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200


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
        content_type="application/vnd.api+json"
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
def test_restore_password(client, user_factory):
    u = user_factory()
    client.force_authenticate(user=u)

    payload = {
        "data": {
            "type": "RestorePasswordModel",
            "attributes": {"username": u.username},
        }
    }

    response = client.post(
        "/users/me/restore_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_reset_password(client, user_factory, default_password_factory, reset_password_token_factory):
    password = Faker().password(length=8, digits=True, upper_case=True)
    dp = default_password_factory()
    dp.set_password(password)
    dp.save()
    u = user_factory()
    token = reset_password_token_factory(user=u)

    response = client.get(
        f"/reset_password/{token}/",
        content_type="application/vnd.api+json"
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
        "/reset_password/asd/",
        content_type="application/vnd.api+json"
    )

    assert response.status_code == 400
