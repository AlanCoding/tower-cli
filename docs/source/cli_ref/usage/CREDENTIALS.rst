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

    tower-cli credential modify --name="new_cred" --ssh-key-data=docs/source/cli_ref/examples/data/insecure_private_key

Doing this will put data defined in the file into the `ssh_key_data` key in the
inputs.
