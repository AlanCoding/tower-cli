import pytest

from awx.api.versioning import reverse

from tower_cli.conf import settings
from tower_cli import get_resource


@pytest.mark.django_db
def test_create_org(admin):
    with settings.runtime_values(host='connection: local', username=admin.username):
        org_res = get_resource('organization')
        r = org_res.create(name='an-org-created')
    assert r['name'] == 'an-org-created'


@pytest.mark.django_db
def test_read_org(organization, admin):
    with settings.runtime_values(host='connection: local', username=admin.username):
        org_res = get_resource('organization')
        r = org_res.get(name='an-org')
    assert r['name'] == organization.name

