import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_user_view(client, user_factory, administrator):
    user = user_factory()
    client.force_authenticate(user=administrator)

    response = client.get(
        '/users',
        content_type="application/vnd.api+json"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
