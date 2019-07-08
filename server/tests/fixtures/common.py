# -*- coding:utf-8 -*-
from rest_framework.test import APIClient

import pytest


@pytest.fixture
def client():
    client = APIClient()
    return client
