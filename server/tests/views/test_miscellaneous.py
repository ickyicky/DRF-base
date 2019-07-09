import pytest
import json
from django.core import management
from django.conf import settings

@pytest.mark.django_db
def test_init_data(client):
    management.call_command("init_data")

    payload = {
        "data": {
            "type": "TokenModel",
            "attributes": {"username": "administrator", "password": "AdMiNi!2#"},
        }
    }

    response = client.post(
        "/cookie", json.dumps(payload), content_type="application/vnd.api+json"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_no_page(client, administrator, user_factory):
    client.force_authenticate(user=administrator)

    for i in range(100):
        user_factory()

    response = client.get(
        '/users',
        content_type="application/vnd.api+json"
    )

    data = response.json()
    assert 'meta' in data
    assert 'pagination' in data['meta']
    assert len(data['data']) == settings.REST_FRAMEWORK["PAGE_SIZE"]

    response = client.get(
        '/users?no_page',
        content_type="application/vnd.api+json"
    )

    data = response.json()
    assert not 'meta' in data
    assert len(data['data']) == 101
