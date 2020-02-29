# -*- coding:utf-8 -*-
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    class client_wrapper(APIClient):
        def post(self, *args, **kwargs):
            kwargs.update(content_type="application/json")
            return super().post(*args, **kwargs)

        def get(self, *args, **kwargs):
            kwargs.update(content_type="application/json")
            return super().get(*args, **kwargs)

        def patch(self, *args, **kwargs):
            kwargs.update(content_type="application/json")
            return super().patch(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.update(content_type="application/json")
            return super().delete(*args, **kwargs)

    return client_wrapper()
