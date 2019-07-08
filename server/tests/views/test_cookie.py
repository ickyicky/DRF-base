import json
from pprint import pprint

import pytest
from faker import Faker


@pytest.mark.django_db
def test_invalid_login(client):
    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": "asd", "password": "asd"},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_remember_me(client, user_factory):
    u = user_factory()
    password = Faker().password(length=8, digits=True, upper_case=True)
    u.set_password(password)
    u.save()

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

    payload["data"]["attributes"]["remember_me"] = True

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200

    response = client.delete(
        "/cookie", cookies=response.cookies, content_type="application/vnd.api+json"
    )

    assert response.status_code == 204
