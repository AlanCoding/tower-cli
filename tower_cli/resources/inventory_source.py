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

import click

from tower_cli import models, resources
from tower_cli.api import client
from tower_cli.utils import debug, types, exceptions as exc


class Resource(models.Resource, models.MonitorableResource):
    cli_help = 'Manage inventory sources within Ansible Tower.'
    endpoint = '/inventory_sources/'
    unified_job_type = '/inventory_updates/'
    identity = ('inventory', 'name')

    name = models.Field()
    credential = models.Field(
        type=types.Related('credential'), required=False, display=True)
    source = models.Field(
        default=None, display=True,
        help_text='The type of inventory source in use.',
        type=click.Choice(['', 'file', 'ec2', 'rax', 'vmware',
                           'gce', 'azure', 'azure_rm', 'openstack',
                           'satellite6', 'cloudforms', 'custom', 'scm']),
    )
    verbosity = models.Field(
        display=False,
        type=types.MappedChoice([
            (0, 'WARNING'),
            (1, 'INFO'),
            (2, 'DEBUG'),
        ]),
        required=False,
    )
    source_regions = models.Field(required=False, display=False)
    # Variables not shared by all cloud providers
    source_vars = models.Field(required=False, display=False)
    instance_filters = models.Field(required=False, display=False)
    group_by = models.Field(required=False, display=False)
    source_script = models.Field(type=types.Related('inventory_script'),
                                 required=False, display=False)
    # Boolean variables
    overwrite = models.Field(type=bool, required=False, display=False)
    overwrite_vars = models.Field(type=bool, required=False, display=False)
    update_on_launch = models.Field(type=bool, required=False, display=False)
    # Only used if update_on_launch is used
    update_cache_timeout = models.Field(type=int, required=False,
                                        display=False)
    timeout = models.Field(type=int, required=False, display=False,
                           help_text='The timeout field (in seconds).')
    inventory = models.Field(
        type=types.Related('inventory'),
        required=False, display=True)
    source_project = models.Field(
        type=types.Related('project'),
        help_text='Use project files as source for inventory.',
        required=False, display=False)
    source_path = models.Field(
        required=False, display=False,
        help_text='File in SCM Project to use as source.')
    update_on_project_update = models.Field(
        type=bool, required=False, display=False)

    @resources.command
    @click.option('--fail-on-found', default=False,
                  show_default=True, type=bool, is_flag=True,
                  help='If used, return an error if a matching record already '
                       'exists.')
    @click.option('--force-on-exists', default=False,
                  show_default=True, type=bool, is_flag=True,
                  help='If used, if a match is found on unique fields, other '
                       'fields will be updated to the provided values. If '
                       'False, a match causes the request to be a no-op.')
    def create(self, **kwargs):
        """Create an object.

        Fields in the resource's `identity` tuple are used for a lookup;
        if a match is found, then no-op (unless `force_on_exists` is set) but
        do not fail (unless `fail_on_found` is set).
        """
        return self.write(create_on_missing=True, **kwargs)

    @click.option('--monitor', is_flag=True, default=False,
                  help='If sent, immediately calls `monitor` on the newly '
                       'launched job rather than exiting with a success.')
    @click.option('--wait', is_flag=True, default=False,
                  help='Polls server for status, exists when finished.')
    @click.option('--timeout', required=False, type=int,
                  help='If provided with --monitor, this command (not the job)'
                       ' will time out after the given number of seconds. '
                       'Does nothing if --monitor is not sent.')
    @resources.command(no_args_is_help=True)
    def update(self, pk, monitor=False, wait=False,
               timeout=None, **kwargs):
        """Update the given inventory source."""

        if pk:
            inventory_source = pk
        else:
            inventory_source = self.get(**kwargs)['id']

        # Establish that we are able to update this inventory source
        # at all.
        debug.log('Asking whether the inventory source can be updated.',
                  header='details')
        r = client.get('%s%d/update/' % (self.endpoint, inventory_source))
        if not r.json()['can_update']:
            raise exc.BadRequest('Tower says it cannot run an update against '
                                 'this inventory source.')

        # Run the update.
        debug.log('Updating the inventory source.', header='details')
        r = client.post('%s%d/update/' % (self.endpoint, inventory_source),
                        data={})

        # If we were told to monitor the project update's status, do so.
        if monitor or wait:
            inventory_update_id = r.json()['inventory_update']
            if monitor:
                result = self.monitor(
                    inventory_update_id, parent_pk=inventory_source,
                    timeout=timeout)
            elif wait:
                result = self.wait(
                    inventory_update_id, parent_pk=inventory_source,
                    timeout=timeout)
            inventory = client.get('/inventory_sources/%d/' %
                                   result['inventory_source'])\
                              .json()['inventory']
            result['inventory'] = int(inventory)
            return result

        # Done.
        return {'status': 'ok'}

    @resources.command
    @click.option('--detail', is_flag=True, default=False,
                  help='Print more detail.')
    def status(self, pk, detail=False, **kwargs):
        """Print the status of the most recent sync."""
        # Obtain the most recent inventory sync
        job = self.last_job_data(pk, **kwargs)

        # In most cases, we probably only want to know the status of the job
        # and the amount of time elapsed. However, if we were asked for
        # verbose information, provide it.
        if detail:
            return job

        # Print just the information we need.
        return {
            'elapsed': job['elapsed'],
            'failed': job['failed'],
            'status': job['status'],
        }
