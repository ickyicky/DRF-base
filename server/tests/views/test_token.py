import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_token_expiration_after_password_change(client, user_factory):
    password = Faker().password(length=8, digits=True, upper_case=True)
    u = user_factory()
    u.set_password(password, silent=True)
    u.save()

    def test_valid(client, status_code):
        response = client.get("/users", content_type="application/vnd.api+json")

        assert response.status_code == status_code

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password},
        }
    }

    response = client.post(
        "/token", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200

    refresh, access = response.json()["data"].values()

    client.credentials(HTTP_AUTHORIZATION="Bearer " + access)

    test_valid(client, 200)

    new_pass = Faker().password(length=8, digits=True, upper_case=True)

    payload = {
        "data": {
            "type": "ChangePasswordModel",
            "attributes": {"old_password": password, "new_password": new_pass},
        }
    }

    response = client.post(
        "/users/me/change_password",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    test_valid(client, 401)

    payload = {
        "data": {"type": "TokenRefreshModel", "attributes": {"refresh_token": refresh}}
    }

    response = client.post(
        "/token/refresh", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_token_refresh(client, user_factory):
    u = user_factory()
    password = Faker().password(length=8, digits=True, upper_case=True)
    u.set_password(password, silent=True)
    u.save()

    def test_valid(client, status_code):
        response = client.get("/users", content_type="application/vnd.api+json")

        assert response.status_code == status_code

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password},
        }
    }

    response = client.post(
        "/token", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200

    refresh, access = response.json()["data"].values()

    client.credentials(HTTP_AUTHORIZATION="Bearer " + access)

    test_valid(client, 200)

    payload = {
        "data": {"type": "TokenRefreshModel", "attributes": {"refresh_token": refresh}}
    }

    response = client.post(
        "/token/refresh", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200

    access = response.json()["data"]["access"]

    client.credentials(HTTP_AUTHORIZATION="Bearer " + access)

    test_valid(client, 200)


@pytest.mark.django_db
def test_token_invalid_password(client, user_factory):
    password = Faker().password(length=8, digits=True, upper_case=True)
    u = user_factory()
    u.set_password(password, silent=True)
    u.save()

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": u.username, "password": password + "a"},
        }
    }

    response = client.post(
        "/token", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 400
