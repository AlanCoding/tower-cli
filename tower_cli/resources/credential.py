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

from tower_cli import models, exceptions as exc
from tower_cli.cli import types


PROMPT = '[Type "ASK" to make this field promptable]'


class InputShortcutField(models.Field):

    def __init__(self, **kwargs):
        kwargs.setdefault('help_text', '')
        kwargs['help_text'] = '[SHORTCUT] will be applied to inputs. ' + kwargs['help_text']
        kwargs.setdefault('display', False)
        super(InputShortcutField, self).__init__(**kwargs)


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
    username = InputShortcutField(
        help_text='The username.',
        required=False,
    )
    password = InputShortcutField(
        help_text='%sThe password. For AWS credentials, the secret key. '
                  'For Rackspace credentials, the API key.' % PROMPT,
        password=True,
        required=False,
    )
    ssh_key_data = InputShortcutField(
        display=False,
        help_text="The full path to the SSH private key to store. "
                  "(Don't worry; it's encrypted.)",
        required=False,
        type=models.File('r'),
    )
    ssh_key_unlock = InputShortcutField(
        help_text='%sssh_key_unlock' % PROMPT,
        password=True, required=False
    )

    def update_from_existing(self, kwargs, existing_data):
        inputs = {}
        if kwargs.get('inputs'):
            inputs = kwargs['inputs'].copy()
        elif existing_data.get('inputs'):
            inputs = existing_data['inputs'].copy()

        need_modification = False
        for field in self.fields:
            if isinstance(field, InputShortcutField):
                new_val = kwargs.pop(field.name, None)
                if not new_val:
                    continue
                need_modification = True
                if kwargs and kwargs.get('inputs', {}).get(field.name):
                    raise exc.BadRequest(
                        'Field {} specified in both shortcut and --inputs.'.format(field.name)
                    )
                inputs[field.name] = new_val

        if need_modification:
            kwargs['inputs'] = inputs
