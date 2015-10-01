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

from __future__ import absolute_import, unicode_literals

import click

from tower_cli import models, resources
from tower_cli.api import client
from tower_cli.utils import debug, exceptions as exc, types


class Resource(models.ExeResource):
    """A resource for ad hoc commands."""
    cli_help = 'Launch commands based on playbook given at runtime.'
    endpoint = '/ad_hoc_commands/'

    # Parameters similar to job
    name = models.Field(unique=True)
    job_explanation = models.Field(required=False, display=False)
    created = models.Field(required=False, display=True)
    status = models.Field(required=False, display=True)
    elapsed = models.Field(required=False, display=True)

    # Parameters similar to job_template
    job_type = models.Field(
        default='run',
        display=False,
        show_default=True,
        type=click.Choice(['run', 'check']),
    )
    inventory = models.Field(type=types.Related('inventory'))
    machine_credential = models.Field(
        'credential',
        display=False,
        type=types.Related('credential'),
    )
    cloud_credential = models.Field(type=types.Related('credential'),
                                    required=False, display=False)
    module_name = models.Field(required=False, display=True,
                               default="command", show_default=True)
    module_args = models.Field(required=False, display=False)
    forks = models.Field(type=int, required=False, display=False)
    limit = models.Field(required=False, display=True)
    verbosity = models.Field(
        display=False,
        type=types.MappedChoice([
            (0, 'default'),
            (1, 'verbose'),
            (2, 'debug'),
        ]),
        required=False,
    )
    become_enabled = models.Field(type=bool, required=False, display=False)

    @resources.command(
        use_fields_as_options=(
            'job_explanation', 'job_type', 'inventory', 'machine_credential',
            'cloud_credential', 'module_name', 'module_args', 'forks',
            'limit', 'verbosity', 'become_enabled',
        )
    )
    @click.option('--monitor', is_flag=True, default=False,
                  help='If sent, immediately calls `job monitor` on the newly '
                       'launched command rather than exiting with a success.')
    @click.option('--timeout', required=False, type=int,
                  help='If provided with --monitor, this attempt'
                       ' will time out after the given number of seconds. '
                       'Does nothing if --monitor is not sent.')
    def launch(self, monitor=False, timeout=None, **kwargs):
        """Launch a new ad-hoc command.

        Runs a user-defined command from Ansible Tower, immediately starts it,
        and returns back an ID in order for its status to be monitored.
        """
        # This feature only exists for versions 2.2 and up
        r = client.get('/')
        if 'ad_hoc_commands' not in r.json():
            raise exc.TowerCLIError('Your host is running an outdated version'
                                    'of Ansible Tower that can not run '
                                    'ad-hoc commands (2.2 or earlier)')

        # Pop the None arguments because we have no .write() method in
        # inheritance chain for this type of resource. This is needed
        self._pop_none(kwargs)

        # Actually start the job.
        debug.log('Launching the ad-hoc command.', header='details')
        result = client.post(self.endpoint, data=kwargs)
        job = result.json()
        job_id = job['id']

        # If we were told to monitor the job once it started, then call
        # monitor from here.
        if monitor:
            return self.monitor(job_id, timeout=timeout)

        # Return the job ID.
        return {
            'changed': True,
            'id': job_id,
        }
