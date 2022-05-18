# Copyright Red Hat
# SPDX-License-Identifier: Apache-2.0
# Author: Guillaume Abrioux <gabrioux@redhat.com>

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
try:
    from ansible.module_utils.ceph_common import exit_module, build_cmd  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module, build_cmd  # type: ignore

import datetime

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_orch
short_description: Ansible cephadm/orch wrapper
version_added: "2.10"
description:
    - Run Ceph commands through Ansible
options:
    fsid:
        description:
            - the fsid of the Ceph cluster to interact with.
        required: false
    cli_binary:
        description:
            - Run a `cephadm` command from the binary.
              See cephadm --help
        required: false
        default: false
    command:
        description:
            - The command to be executed.
        required: true
    stdin:
        description:
            - data to be passed to stdin
        required: false

author:
    - Guillaume Abrioux <gabrioux@redhat.com>
'''

EXAMPLES = '''
- name: bootstrap initial cluster
  ceph_orch:
    cli_binary: true
    command: "cephadm bootstrap --fsid 3c9ba63a-c7df-4476-a1e7-317dfc711f82 --mon-ip 1.2.3.4 --skip-pull"

- name: get the cephadm ssh pub key
  ceph_orch:
    command: "cephadm get-pub-key"
  register: pub_key

- name: add a host
  ceph_orch:
    command: "orch host add ceph-node-01"
'''

RETURN = '''#  '''


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            cli_binary=dict(type='bool', required=False, default=False),
            command=dict(type='str', required=True),
            stdin=dict(type='str', required=False, default=None),
            fsid=dict(type='str', required=False)
        ),
        supports_check_mode=True,
    )

    # Gather module parameters in variables
    cli_binary = module.params.get('cli_binary')
    command = module.params.get('command')
    stdin = module.params.get('stdin')

    if module.check_mode:
        module.exit_json(
            changed=False,
            stdout='',
            stderr='',
            rc=0,
            start='',
            end='',
            delta='',
        )

    startd = datetime.datetime.now()

    cmd = build_cmd(module, cli_binary, command)
    rc, out, err = module.run_command(cmd, data=stdin)

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd)


if __name__ == '__main__':
    main()
