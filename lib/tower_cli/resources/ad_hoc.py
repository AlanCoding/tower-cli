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
from distutils.version import LooseVersion

import click

from sdict import adict

from tower_cli import models, resources
from tower_cli.api import client
from tower_cli.utils import debug, exceptions as exc, types


class Resource(models.ReadableResource, models.MonitorableResource):
    """A resource for ad hoc commands."""
    cli_help = 'Launch or monitor  without template.'
    endpoint = '/ad_hoc_commands/'

    # Many parameter fields are similiar to job template, as opposed to job
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
    module_name = models.Field(required=False, display=False,
                               default="command")
    module_args = models.Field(required=False, display=False, default="")
    forks = models.Field(type=int, default=0, required=False, display=False)
    limit = models.Field(required=False, display=False, default="")
    verbosity = models.Field(
        default="default",
        display=False,
        type=types.MappedChoice([
            (0, 'default'),
            (1, 'verbose'),
            (2, 'debug'),
        ]),
        required=False,
    )
    become_enabled = models.Field(type=bool, required=False, display=False,
                                  show_default=True, default=False)

    @resources.command
    @click.option('--monitor', is_flag=True, default=False,
                  help='If sent, immediately calls `job monitor` on the newly '
                       'launched job rather than exiting with a success.')
    @click.option('--timeout', required=False, type=int,
                  help='If provided with --monitor, this command (not the job)'
                       ' will time out after the given number of seconds. '
                       'Does nothing if --monitor is not sent.')
    def launch(self, monitor=False, timeout=None, **kwargs):
        """Launch a new job based on ad-hoc tasks.

        Creates a new job in Ansible Tower, immediately starts it, and
        returns back an ID in order for its status to be monitored.
        """
        # This feature only exists for versions 2.2 and up
        r = client.get('/config/')
        if LooseVersion(r.json()['version']) < LooseVersion('2.2'):
            raise exc.TowerCLIError('Your host is running an outdated version'
                                    'of Ansible Tower that can not run '
                                    'ad-hoc commands')

        # Actually start the job.
        debug.log('Launching the ad-hoc job.', header='details')
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

    @resources.command
    @click.option('--detail', is_flag=True, default=False,
                  help='Print more detail.')
    def status(self, pk, detail=False):
        """Print the current job status."""
        # Get the job from Ansible Tower.
        debug.log('Asking for ad-hoc job status.', header='details')
        finished_endpoint = self.endpoint + str(pk) + "/"
        job = client.get(finished_endpoint).json()

        # In most cases, we probably only want to know the status of the job
        # and the amount of time elapsed. However, if we were asked for
        # verbose information, provide it.
        if detail:
            return job

        # Print just the information we need.
        return adict({
            'elapsed': job['elapsed'],
            'failed': job['failed'],
            'status': job['status'],
        })

    @resources.command
    @click.option('--fail-if-not-running', is_flag=True, default=False,
                  help='Fail loudly if the job is not currently running.')
    def cancel(self, pk, fail_if_not_running=False):
        """Cancel a currently running job.

        Fails with a non-zero exit status if the job cannot be canceled.
        """
        cancel_endpoint = self.endpoint + str(pk) + "/cancel/"
        # Attempt to cancel the job.
        try:
            client.post(cancel_endpoint)
            changed = True
        except exc.MethodNotAllowed:
            changed = False
            if fail_if_not_running:
                raise exc.TowerCLIError('Job not running.')

        # Return a success.
        return adict({'status': 'canceled', 'changed': changed})
