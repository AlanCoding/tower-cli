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
from tower_cli.utils import types


class Resource(models.Resource):
    cli_help = 'Manage hosts belonging to a group within an inventory.'
    endpoint = '/hosts/'
    identity = ('inventory', 'name')

    name = models.Field(unique=True)
    description = models.Field(required=False, display=False)
    inventory = models.Field(type=types.Related('inventory'))
    enabled = models.Field(type=bool, required=False)
    variables = models.Field(
        type=types.Variables(), required=False, display=False,
        help_text='Host variables, use "@" to get from file.')
    group = models.Field(
        type=types.ManyRelated('group', relationship='groups'))

    @resources.command(use_fields_as_options=False)
    @click.option('--host', type=types.Related('host'))
    @click.option('--group', type=types.Related('group'))
    @click.option('--host-name', type=types.Related('host',
                  convert_digits=False))
    @click.option('--group-name', type=types.Related('group',
                  convert_digits=False))
    def associate(self, host, group, host_name, group_name):
        """Associate a group with this host."""
        if host_name and not host:
            host = host_name
        if group_name and not group:
            group = group_name
        return self._assoc('groups', host, group)

    @resources.command(use_fields_as_options=False)
    @click.option('--host', type=types.Related('host'))
    @click.option('--group', type=types.Related('group'))
    @click.option('--host-name', type=types.Related('host',
                  convert_digits=False))
    @click.option('--group-name', type=types.Related('group',
                  convert_digits=False))
    def disassociate(self, host, group, host_name, group_name):
        """Disassociate a group from this host."""
        if host_name and not host:
            host = host_name
        if group_name and not group:
            group = group_name
        return self._disassoc('groups', host, group)

    @resources.command(ignore_defaults=True, no_args_is_help=False)
    @click.option('--group', type=types.Related('group'),
                  help='List hosts that are children of this group.')
    def list(self, group=None, **kwargs):
        """Return a list of hosts.
        """
        if group:
            kwargs['query'] = (kwargs.get('query', ()) +
                               (('groups__in', group),))
        return super(Resource, self).list(**kwargs)
