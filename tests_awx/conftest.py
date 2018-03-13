# Python
import pytest

# Django
from django.core.urlresolvers import resolve
from django.utils.six.moves.urllib.parse import urlparse
from django.contrib.auth.models import User

from rest_framework.test import (
    APIRequestFactory,
    force_authenticate,
)

# AWX
from awx.main.models import User


@pytest.fixture
def admin():
    return User.objects.create(username='admin_user', is_superuser=True)


def _request(verb):
    def rf(url, data_or_user=None, user=None, middleware=None, expect=None, **kwargs):
        if type(data_or_user) is User and user is None:
            user = data_or_user
        elif 'data' not in kwargs:
            kwargs['data'] = data_or_user
        if 'format' not in kwargs and 'content_type' not in kwargs:
            kwargs['format'] = 'json'

        view, view_args, view_kwargs = resolve(urlparse(url)[2])
        request = getattr(APIRequestFactory(), verb)(url, **kwargs)
        if isinstance(kwargs.get('cookies', None), dict):
            for key, value in kwargs['cookies'].items():
                request.COOKIES[key] = value
        if middleware:
            middleware.process_request(request)
        if user:
            force_authenticate(request, user=user)

        response = view(request, *view_args, **view_kwargs)
        if middleware:
            middleware.process_response(request, response)
        if expect:
            if response.status_code != expect:
                if getattr(response, 'data', None):
                    try:
                        data_copy = response.data.copy()
                        # Make translated strings printable
                        for key, value in response.data.items():
                            if isinstance(value, list):
                                response.data[key] = []
                                for item in value:
                                    response.data[key].append(str(item))
                            else:
                                response.data[key] = str(value)
                    except Exception:
                        response.data = data_copy
            assert response.status_code == expect
        if hasattr(response, 'render'):
            response.render()
        return response
    return rf


@pytest.fixture
def post():
    return _request('post')


@pytest.fixture
def get():
    return _request('get')


@pytest.fixture
def put():
    return _request('put')


@pytest.fixture
def patch():
    return _request('patch')


@pytest.fixture
def delete():
    return _request('delete')


@pytest.fixture
def head():
    return _request('head')


@pytest.fixture
def options():
    return _request('options')
