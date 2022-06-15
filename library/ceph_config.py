# Copyright Red Hat
# SPDX-License-Identifier: Apache-2.0
# Author: Guillaume Abrioux <gabrioux@redhat.com>

from __future__ import absolute_import, division, print_function
from typing import List, Tuple
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
try:
    from ansible.module_utils.ceph_common import exit_module, build_base_cmd_shell, fatal  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module, build_base_cmd_shell, fatal  # type: ignore

import datetime

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_config
short_description: set ceph config
version_added: "2.10"
description:
    - Set Ceph config options.
options:
    fsid:
        description:
            - the fsid of the Ceph cluster to interact with.
        required: false
    image:
        description:
            - The Ceph container image to use.
        required: false
    action:
        description:
            - whether to get or set the parameter specified in 'option'
        required: false
        default: 'set'
    who:
        description:
            - which daemon the configuration should be set to
        required: true
    option:
        description:
            - name of the parameter to be set
        required: true
    value:
        description:
            - value of the parameter
        required: true if action is 'set'

author:
    - Guillaume Abrioux <gabrioux@redhat.com>
'''

EXAMPLES = '''
- name: set osd_memory_target for osd.0
  ceph_config:
    action: set
    who: osd.0
    option: osd_memory_target
    value: 5368709120

- name: set osd_memory_target for host ceph-osd-02
  ceph_config:
    action: set
    who: osd/host:ceph-osd-02
    option: osd_memory_target
    value: 5368709120

- name: get osd_pool_default_size value
  ceph_config:
    action: get
    who: global
    option: osd_pool_default_size
    value: 1
'''

RETURN = '''#  '''


def get_or_set_option(module: "AnsibleModule",
                      action: str,
                      who: str,
                      option: str,
                      value: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'config', action, who, option])

    if action == 'set':
        cmd.append(value)

    rc, out, err = module.run_command(cmd)

    return rc, cmd, out.strip(), err


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            who=dict(type='str', required=True),
            action=dict(type='str', required=False, choices=['get', 'set'], default='set'),
            option=dict(type='str', required=True),
            value=dict(type='str', required=False),
            fsid=dict(type='str', required=False),
            image=dict(type='str', required=False)
        ),
        supports_check_mode=True,
        required_if=[['action', 'set', ['value']]]
    )

    # Gather module parameters in variables
    who = module.params.get('who')
    option = module.params.get('option')
    value = module.params.get('value')
    action = module.params.get('action')

    if module.check_mode:
        module.exit_json(
            changed=False,
            stdout='',
            cmd=[],
            stderr='',
            rc=0,
            start='',
            end='',
            delta='',
        )

    startd = datetime.datetime.now()
    changed = False

    rc, cmd, out, err = get_or_set_option(module, 'get', who, option, value)
    if rc:
        fatal(message=f"Can't get current value. who={who} option={option}", module=module)

    if action == 'set':
        if value.lower() == out:
            out = 'who={} option={} value={} already set. Skipping.'.format(who, option, value)
        else:
            rc, cmd, out, err = get_or_set_option(module, action, who, option, value)
            changed = True

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd,
                changed=changed)


if __name__ == '__main__':
    main()
