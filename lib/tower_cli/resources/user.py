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

from tower_cli import models, get_resource, resources
from tower_cli.utils import debug, types


class Resource(models.WritableResource):
    cli_help = 'Manage users within Ansible Tower.'
    endpoint = '/users/'
    identity = ('username',)

    username = models.Field(unique=True)
    password = models.Field(required=False, display=False)
    email = models.Field(unique=True)
    first_name = models.Field(required=False)
    last_name = models.Field(required=False)
    is_superuser = models.Field(required=False, type=bool)

    organization = models.Field(type=types.Related('organization'),
                                display=False, required=False)

    @resources.command
    def create(self, organization=None, *args, **kwargs):
        """Create a new item of resource, with or w/o org.
        """
        backup_endpoint = self.endpoint
        if organization:
            debug.log("using alternative endpoint specific to organization",
                      header='details')

            # Get the organization from Tower, will lookup name if needed
            org_resource = get_resource('organization')
            org_data = org_resource.get(organization)
            org_pk = org_data['id']

            self.endpoint = '/organizations/%s%s' % (org_pk, backup_endpoint)
        to_return = super(Resource, self).create(*args, **kwargs)
        self.endpoint = backup_endpoint
        return to_return
