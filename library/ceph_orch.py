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


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            cli_binary=dict(type='bool', required=False, default=False),
            command=dict(type='str', required=True),
            stdin=dict(type='str', required=False, default=None),
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

    cmd = build_cmd(cli_binary, command)
    rc, out, err = module.run_command(cmd, data=stdin)

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd)


if __name__ == '__main__':
    main()
