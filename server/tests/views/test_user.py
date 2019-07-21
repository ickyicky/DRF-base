import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_user_get(client, user_factory, administrator):
    user = user_factory()
    client.force_authenticate(user=administrator)

    response = client.get("/users", content_type="application/vnd.api+json")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@pytest.mark.django_db
def test_user_create(client, user_payload, administrator):
    client.force_authenticate(user=administrator)

    response = client.post(
        "/users", json.dumps(user_payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_user_create_too_weak_password(client, user_payload, administrator):
    client.force_authenticate(user=administrator)

    user_payload["data"]["attributes"]["password"] = Faker().password(
        length=8, digits=False, upper_case=True, lower_case=True
    )

    response = client.post(
        "/users", json.dumps(user_payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_patch(client, user_factory, administrator):
    user = user_factory()
    client.force_authenticate(user=administrator)
    name = "Example"

    response = client.get(f"/users/{user.id}", content_type="application/vnd.api+json")

    assert response.status_code == 200

    payload = response.json()
    payload["data"]["attributes"]["last_name"] = name

    response = client.patch(
        f"/users/{user.id}",
        json.dumps(payload),
        content_type="application/vnd.api+json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["attributes"]["last_name"] == name
