import pytest

from awx.api.versioning import reverse

from tower_cli.conf import settings
from tower_cli import get_resource

from awx.main.models import Organization


@pytest.mark.django_db
def test_create_org(post, admin):
    url = reverse('api:organization_list')
    r = post(url, data={'name': 'anorg'}, user=admin, expect=201)


@pytest.fixture
def organization():
    return Organization.objects.create(name='an-org')


@pytest.mark.django_db
def test_read_org(organization, admin):
    with settings.runtime_values(host='connection: local', username=admin.username):
        org_res = get_resource('organization')
        r = org_res.get(name='an-org')
    assert r['name'] == organization.name

