import json
import pytest
import random
from api.models.user import Role
from ..fixtures.user import generate_username


@pytest.mark.parametrize('role', [
    (Role.ADMINISTRATOR.name, 201, 200),
    (Role.USER.name, 403, 403),
])
@pytest.mark.django_db
def test_administrator_permissions(client, role, user_factory, user_attributes):
    for _ in range(10):
        user_factory()

    user = user_factory(role=role[0])
    client.force_authenticate(user=user)

    response = client.get(
        "/users"
    )
    assert response.status_code == 200

    ids = [u["id"] for u in response.json()]
    random_id = user.id
    while random_id == user.id:
        random_id = int(random.choice(ids))

    response = client.get(
        f"/users/{random_id}"
    )
    assert response.status_code == 200

    response = client.post(
        "/users",
        json.dumps(user_attributes)
    )
    assert response.status_code == role[1]

    response = client.patch(
        f"/users/{random_id}",
        json.dumps({"username": generate_username()})
    )
    assert response.status_code == role[2]

    response = client.get(
        f"/users/{user.id}",
    )
    assert response.status_code == 200
