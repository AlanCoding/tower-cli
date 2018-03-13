import pytest

from awx.api.versioning import reverse


@pytest.mark.django_db
def test_create_org(post, admin):
    url = reverse('api:organization_list')
    r = post(url, data={'name': 'anorg'}, user=admin, expect=201)
