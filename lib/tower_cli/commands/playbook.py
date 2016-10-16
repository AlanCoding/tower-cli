# Copyright 2015, Ansible by Red Hat
# Alan Rominger <arominge@redhat.com>
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

# new imports
import tower_cli
from tower_cli.conf import Parser, settings

# old imports
from tower_cli.api import client
from tower_cli.utils.decorators import command
from tower_cli.utils.exceptions import TowerCLIError


@command
@click.argument('playbook', required=False)
@click.option('--limit', help='Subset of hosts/groups to run on.')
@click.option('--check', is_flag=True, help='Run job in check mode.')
@click.option('--extra_vars', multiple=True, help='variables to pass into the playbook.')
def playbook(playbook, limit=None, check=False, extra_vars=None):
    """
    Create resources to run a playbook on Ansible Tower, update the SCM,
    and then run the job in a single command.
    Designed to follow a similar invocation method as ansible-playbook
    tower-cli playbook hello_world.yml --limit "webservers" -e "a=4"
    The inventory and credential need to be specified in the .tower_sync.cfg
    file within the current working directory.
    """
    filename = '.tower_sync.cfg'
    parser = Parser()
    parser.add_section('general')
    parser.read(filename)
    
    project = None
    inventory = None
    credential = None
    
    # import pdb; pdb.set_trace()

    # Print out the current version of Tower CLI.
    click.echo('Using configuration file with %s inventory and %s credential.' % (inventory, credential))

