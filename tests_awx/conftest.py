# Python
import pytest

# Django
from django.core.urlresolvers import resolve
from django.utils.six.moves.urllib.parse import urlparse

from rest_framework.test import (
    APIRequestFactory,
    force_authenticate,
)

# AWX
from awx.main.models import User, Organization


@pytest.fixture
def admin():
    return User.objects.create(username='admin_user', is_superuser=True)


@pytest.fixture
def organization():
    return Organization.objects.create(name='an-org')
