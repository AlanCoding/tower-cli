.. _cli_ref:

Credential Management
=====================

Credential Types and Inputs
-----------------------------

Starting in Ansible Tower 3.2, credential have types defined by a
related table of credential types. Credential types have a name,
kind, and primary key, and can be referenced uniquely by either the
primary key or combination of (name, kind).

Data that the credential contains is embedded in the JSON-type
field ``inputs``. The way to create a credential via the type and
inputs pattern is the following:

::

    tower-cli credential create --name="new_cred" --inputs="{username: foo, password: bar}" --credential-type="Machine" --organization="Default"

This method of specifying fields is most congruent with the modern Tower API.


Field Shortcuts
---------------

There are some drawbacks to specifying fields inside of YAML / JSON content
inside of another field. Shortcuts are offered as a way around those.

The most important problem this solves is specifying multi-line input
from a file. This example can be ran from the project root:

::

    tower-cli credential modify --name="new_cred" --subinput ssh_key_data @docs/source/cli_ref/examples/data/insecure_private_key
    tower-cli credential create --name="only_ssh_key" --subinput ssh_key_data @docs/source/cli_ref/examples/data/insecure_private_key --credential-type="Machine" --organization="Default"

Doing this will put data defined in the file into the `ssh_key_data` key in the
inputs.

The ``--subinput`` option will also perform some conditional type coercion.
At present time, this only matters for boolean type inputs, allowing actions
like the following.

::

    tower-cli credential create --name="tower_cred" --inputs="{host: foo.invalid, username: foo, password: bar}" --credential-type="Ansible Tower" --organization=Default
    tower-cli credential modify --name=tower_cred --subinput verify_ssl true

In both cases, the point of the ``--subinput`` field is that changing one
field will still perserve the others. For instance, toggling the value of
``verify_ssl`` will not change the value of the ``host`` input.
