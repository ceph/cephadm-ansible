# Copyright Red Hat
# SPDX-License-Identifier: Apache-2.0
# Author: Guillaume Abrioux <gabrioux@redhat.com>

from __future__ import absolute_import, division, print_function
from typing import List, Tuple
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
try:
    from ansible.module_utils.ceph_common import retry, exit_module, build_base_cmd_orch, fatal  # type: ignore
except ImportError:
    from module_utils.ceph_common import retry, exit_module, build_base_cmd_orch, fatal  # type: ignore

import datetime
import json

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_orch_daemon
short_description: stop/start daemon
version_added: "2.9"
description:
    - Start, stop or restart ceph daemon
options:
    fsid:
        description:
            - the fsid of the Ceph cluster to interact with.
        required: false
    image:
        description:
            - The Ceph container image to use.
        required: false
    state:
        description:
            - The desired state of the service specified in 'name'.
              If 'started', it ensures the service is started.
              If 'stopped', it ensures the service is stopped.
              If 'restarted', it will restart the service.
        required: True
    daemon_id:
        description:
            - The id of the service.
        required: true
    daemon_type:
        description:
            - The type of the service.
        required: true

author:
    - Guillaume Abrioux <gabrioux@redhat.com>
'''

EXAMPLES = '''
- name: start osd.0
  ceph_orch_daemon:
    state: started
    daemon_id: 0
    daemon_type: osd

- name: stop mon.ceph-node0
  ceph_orch_daemon:
    state: stopped
    daemon_id: ceph-node0
    daemon_type: mon
'''

RETURN = '''#  '''


def get_current_state(module: "AnsibleModule",
                      daemon_type: str,
                      daemon_id: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_orch(module)
    cmd.extend(['ps', '--daemon_type',
                daemon_type, '--daemon_id',
                daemon_id, '--format', 'json',
                '--refresh'])
    rc, out, err = module.run_command(cmd)

    return rc, cmd, out, err


def update_daemon_status(module: "AnsibleModule",
                         action: str,
                         daemon_name: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_orch(module)
    cmd.extend(['daemon', action, daemon_name])
    rc, out, err = module.run_command(cmd)

    return rc, cmd, out, err


@retry(RuntimeError)
def validate_updated_status(module: "AnsibleModule",
                            action: str,
                            daemon_type: str,
                            daemon_id: str) -> None:
    rc, cmd, out, err = get_current_state(module, daemon_type, daemon_id)
    expected_state = 1 if action == 'start' else 0
    if not json.loads(out)[0]['status'] == expected_state:
        raise RuntimeError("Status for {}.{} isn't reported as expected.".format(daemon_type, daemon_id))


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str',
                       required=True,
                       choices=['started', 'stopped', 'restarted']),
            daemon_id=dict(type='str', required=True),
            daemon_type=dict(type='str', required=True),
            docker=dict(type=bool,
                        required=False,
                        default=False),
            fsid=dict(type='str', required=False),
            image=dict(type='str', required=False)
        ),
        supports_check_mode=True,
    )

    # Gather module parameters in variables
    state = module.params.get('state')
    daemon_id = module.params.get('daemon_id')
    daemon_type = module.params.get('daemon_type')
    daemon_name = "{}.{}".format(daemon_type, daemon_id)

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

    rc, cmd, out, err = get_current_state(module, daemon_type, daemon_id)

    if rc or not json.loads(out):
        if not err:
            err = 'osd id {} not found'.format(daemon_id)
        fatal("Can't get current status of {}: {}".format(daemon_name, err), module)

    is_running = json.loads(out)[0]['status'] == 1

    current_state = 'started' if is_running else 'stopped'
    action = 'start' if state == 'started' else 'stop'
    if state == current_state:
        out = "{} is already {}, skipping.".format(daemon_name, state)
    else:
        rc, cmd, out, err = update_daemon_status(module, action, daemon_name)
        validate_updated_status(module, action, daemon_type, daemon_id)
        changed = True

    if state == 'restarted':
        action = 'restart'
        changed = True
        rc, cmd, out, err = update_daemon_status(module, action, daemon_name)

    if rc:
        fatal("Can't {} {}: {}".format(action, daemon_name, err))

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd,
                changed=changed)


if __name__ == '__main__':
    main()
