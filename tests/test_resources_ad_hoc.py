# Copyright 2015, Ansible, Inc.
# Luke Sneeringer <lsneeringer@ansible.com>
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
from tower_cli.utils import exceptions as exc

from tests.compat import unittest, mock


class LaunchTests(unittest.TestCase):
    """A set of tests for ensuring that the ad hoc resource's
    launch command works in the way we expect.
    """
    def setUp(self):
        self.res = tower_cli.get_resource('ad_hoc')

    def test_basic_launch(self):
        """Establish that we are able to create a ad hoc job.
        """
        with client.test_mode as t:
            t.register_json('/ad_hoc_commands/42/', {'id': 42}, method='GET')
            t.register_json('/', {
                'ad_hoc_commands': '/api/v1/ad_hoc_commands/'
                }, method='GET')
            t.register_json('/ad_hoc_commands/', {'id': 42}, method='POST')
            result = self.res.launch(inventory=1, machine_credential=2,
                                     module_args="echo 'hi'")
            self.assertEqual(result, {'changed': True, 'id': 42})

    def test_version_failure(self):
        """Establish that if the job has failed, that we raise the
        JobFailure exception.
        """
        with client.test_mode as t:
            t.register_json('/ad_hoc_commands/42/', {'id': 42}, method='GET')
            t.register_json('/', {}, method='GET')
            t.register_json('/ad_hoc_commands/', {'id': 42}, method='POST')
            with self.assertRaises(exc.TowerCLIError):
                self.res.launch(inventory=1, machine_credential=2,
                                module_args="echo 'hi'")

    def test_basic_launch_monitor_option(self):
        """Establish that we are able to create a job that doesn't require
        any invocation-time input, and that monitor is called if requested.
        """
        with client.test_mode as t:
            t.register_json('/ad_hoc_commands/42/', {'id': 42}, method='GET')
            t.register_json('/', {
                'ad_hoc_commands': '/api/v1/ad_hoc_commands/'
                }, method='GET')
            t.register_json('/ad_hoc_commands/', {'id': 42}, method='POST')

            with mock.patch.object(type(self.res), 'monitor') as monitor:
                self.res.launch(inventory=1, machine_credential=2,
                                module_args="echo 'hi'", monitor=True)
                monitor.assert_called_once_with(42, timeout=None)


class StatusTests(unittest.TestCase):
    """A set of tests to establish that the ad hoc job status command
    works in the way that we expect.
    """
    def setUp(self):
        self.res = tower_cli.get_resource('ad_hoc')

    def test_normal(self):
        """Establish that the data about a ad hoc job retrieved from the jobs
        endpoint is provided.
        """
        with client.test_mode as t:
            t.register_json('/ad_hoc_commands/42/', {
                'elapsed': 1335024000.0,
                'extra': 'ignored',
                'failed': False,
                'status': 'successful',
            })
            result = self.res.status(42)
            self.assertEqual(result, {
                'elapsed': 1335024000.0,
                'failed': False,
                'status': 'successful',
            })
            self.assertEqual(len(t.requests), 1)

    def test_detailed(self):
        with client.test_mode as t:
            t.register_json('/ad_hoc_commands/42/', {
                'elapsed': 1335024000.0,
                'extra': 'ignored',
                'failed': False,
                'status': 'successful',
            })
            result = self.res.status(42, detail=True)
            self.assertEqual(result, {
                'elapsed': 1335024000.0,
                'extra': 'ignored',
                'failed': False,
                'status': 'successful',
            })
            self.assertEqual(len(t.requests), 1)


class CancelTests(unittest.TestCase):
    """A set of tasks to establish that the ad hoc job cancel
    command works in the way that we expect.
    """
    def setUp(self):
        self.res = tower_cli.get_resource('ad_hoc')

    def test_standard_cancelation(self):
        """Establish that a standard cancelation command works in the way
        we expect.
        """
        with client.test_mode as t:
            t.register('/ad_hoc_commands/42/cancel/', '', method='POST')
            result = self.res.cancel(42)
            self.assertTrue(
                t.requests[0].url.endswith('/ad_hoc_commands/42/cancel/')
            )
            self.assertTrue(result['changed'])

    def test_cancelation_completed_with_error(self):
        """Establish that a standard cancelation command works in the way
        we expect.
        """
        with client.test_mode as t:
            t.register('/ad_hoc_commands/42/cancel/', '',
                       method='POST', status_code=405)
            with self.assertRaises(exc.TowerCLIError):
                self.res.cancel(42, fail_if_not_running=True)
