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

import six
import os

from tower_cli import models, exceptions as exc, get_resource
from tower_cli.cli import types
from tower_cli.utils import debug, str_to_bool


class Resource(models.Resource):
    """A resource for credentials."""
    cli_help = 'Manage credentials within Ansible Tower.'
    endpoint = '/credentials/'
    identity = ('organization', 'user', 'team', 'name')
    dependencies = ['organization', 'credential_type']

    name = models.Field(unique=True)
    description = models.Field(required=False, display=False)

    # Who owns this credential?
    user = models.Field(display=False, type=types.Related('user'), required=False, no_lookup=True)
    team = models.Field(display=False, type=types.Related('team'), required=False, no_lookup=True)
    organization = models.Field(display=False, type=types.Related('organization'), required=False)

    # Core functionality
    credential_type = models.Field(type=types.Related('credential_type'))
    inputs = models.Field(type=types.StructuredInput(), required=False, display=False)

    # Fields for reverse compatibility
    subinput = models.Field(
        required=False, nargs=2, multiple=True, display=False,
        help_text='A key and value to be combined into the credential inputs JSON data.'
                  ' Start the value with "@" to obtain from a file.\n'
                  'Example: `--subinput ssh_key_data @filename` would apply an SSH private key'
    )

    def update_from_existing(self, kwargs, existing_data):
        subinputs = kwargs.pop('subinput', ())
        if not subinputs:
            return super(Resource, self).update_from_existing(kwargs, existing_data)

        inputs = {}
        if kwargs.get('inputs'):
            inputs = kwargs['inputs'].copy()
        elif existing_data.get('inputs'):
            inputs = existing_data['inputs'].copy()

        ct_pk = None
        if existing_data:
            ct_pk = existing_data.get('credential_type')
        else:
            ct_pk = kwargs.get('credential_type')
        if not ct_pk:
            debug.log('Could not apply subinputs because of unknown credential type')
            return super(Resource, self).update_from_existing(kwargs, existing_data)

        ct_res = get_resource('credential_type')
        schema = ct_res.get(ct_pk)['inputs'].get('fields', [])
        schema_map = {}
        for element in schema:
            schema_map[element.get('id', '')] = element

        for key, raw_value in subinputs:
            if kwargs and kwargs.get(key, {}).get(key):
                raise exc.BadRequest(
                    'Field {} specified in both --subinput and --inputs.'.format(key)
                )

            # Read from a file if starts with "@"
            if raw_value.startswith('@'):
                filename = os.path.expanduser(raw_value[1:])
                with open(filename, 'r') as f:
                    value = f.read()
            else:
                value = raw_value

            # Type conversion
            if key not in schema_map:
                debug.log('Credential type inputs:\n{}'.format(schema))
                raise exc.BadRequest(
                    'Field {} is not allowed by credential type inputs.'.format(key)
                )
            type_str = schema_map[key].get('type', 'string')

            converters = {
                'string': six.text_type,
                'boolean': str_to_bool
            }
            if type_str not in converters:
                raise exc.BadRequest(
                    'Credential type {} input {} uses an unrecognized type: {}.'.format(
                        ct_pk, key, type_str)
                )
            converter = converters[type_str]
            try:
                value = converter(value)
            except Exception as e:
                raise exc.BadRequest(
                    'Field {} in --subinput is not type {} specified by credential type '
                    '{} inputs.\n(error: {})'.format(key, type_str, ct_pk, e)
                )
            inputs[key] = value
        kwargs['inputs'] = inputs
