# Copyright 2015, Ansible, Inc.
# Alan Rominger <arominger@ansible.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tower_cli
from tower_cli.api import client

from tests.compat import unittest


class CreateTests(unittest.TestCase):
    """Tests to creation of a user under the relevant circumstances.
    """
    def setUp(self):
        self.res = tower_cli.get_resource('user')

    def test_create_with_organization(self):
        """Establish that a user can be created within an organization
        """
        with client.test_mode as t:
            endpoint = '/organizations/1/users/'
            t.register_json(endpoint, {'count': 0, 'results': [],
                            'next': None, 'previous': None},
                            method='GET')
            t.register_json(endpoint, {'changed': True, 'id': 42},
                            method='POST')
            # The organization endpoint used to lookup org pk given org name
            t.register_json('/organizations/1/', {'id': 1}, method='GET')
            result = self.res.create(
                username='bill', password="password",
                organization=1, email="asdf@asdf.com"
            )
            self.assertEqual(t.requests[0].method, 'GET')
            self.assertEqual(t.requests[-1].method, 'POST')
            self.assertDictContainsSubset({'id': 42}, result)

    def test_create_without_organization(self):
        """Establish that a user can be created within an organization
        """
        with client.test_mode as t:
            endpoint = '/users/'
            t.register_json(endpoint, {'count': 0, 'results': [],
                            'next': None, 'previous': None},
                            method='GET')
            t.register_json(endpoint, {'changed': True, 'id': 42},
                            method='POST')
            t.register_json('/users/?username=bill',
                            {'count': 0, 'results': []}, method='GET')
            result = self.res.create(
                username='bill', password="password",
                email="asdf@asdf.com"
            )
            self.assertEqual(t.requests[0].method, 'GET')
            self.assertEqual(t.requests[-1].method, 'POST')
            self.assertDictContainsSubset({'id': 42}, result)
