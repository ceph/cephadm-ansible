from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Tuple, Union
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
try:
    from ansible.module_utils.ceph_common import exit_module, build_base_cmd_shell, fatal  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module, build_base_cmd_shell, fatal  # type: ignore

import datetime
import json

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_config_key
short_description: Ensure a Ceph config-key is present or absent
version_added: ""
description:
    - Manage Ceph config-key entries declaratively. Ensures the given key
      has the specified value (state=present) or is removed (state=absent).
options:
    option:
        type: str
        description:
            - Name of the config-key to manage.
        required: true
    value:
        type: str
        description:
            - Value to set for the config-key. Required when state is present.
        required: true when state is present
    state:
        type: str
        description:
            - Whether the config-key should exist with the given value (present)
              or be removed (absent).
        required: false
        default: present
        choices: [ present, absent ]
    fsid:
        type: str
        description:
            - The fsid of the Ceph cluster to interact with.
        required: false
    image:
        type: str
        description:
            - The Ceph container image to use.
        required: false
'''

EXAMPLES = '''
- name: Ensure config/mgr/mgr/prometheus/scrape_interval is set to 15
  ceph_config_key:
    option: config/mgr/mgr/prometheus/scrape_interval
    value: "15"
    state: present

- name: Set mgr/cephadm/services/prometheus/prometheus.yml from file
  ceph_config_key:
    option: mgr/cephadm/services/prometheus/prometheus.yml
    value: "{{ lookup('file', '/path/to/prometheus.yml') }}"
    state: present

- name: Remove config-key if present
  ceph_config_key:
    option: config/mgr/mgr/prometheus/scrape_interval
    state: absent
'''

RETURN = '''
stdout:
  description: The current value of the config-key after the run (when state is present).
  type: str
  returned: always
'''


def set_config_key_value(module: "AnsibleModule",
                         option: str,
                         value: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'config-key', 'set', option, '-i', '-'])

    # pass the value through stdin to avoid issues with multi-line values, encoding, etc.
    rc, out, err = module.run_command(args=cmd, data=value)

    return rc, cmd, out.strip(), err


def del_config_key(module: "AnsibleModule", option: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'config-key', 'del', option])
    rc, out, err = module.run_command(cmd)
    return rc, cmd, out.strip(), err


def get_config_key_dump(module: "AnsibleModule") -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'config-key', 'dump', '--format', 'json'])
    rc, out, err = module.run_command(cmd)
    if rc:
        fatal(message=f"Can't get current configuration via `ceph config-key dump`.Error:\n{err}", module=module)
    out = out.strip()
    return rc, cmd, out, err


def get_config_key_current_value(option: str, config_dump: Dict[str, Any]) -> Union[str, None]:
    for key in config_dump:
        if key == option:
            v = config_dump[key]
            return v if v is None else str(v)
    return None


def run(module: "AnsibleModule") -> None:
    option = module.params.get('option')
    value = module.params.get('value')
    state = module.params.get('state')

    startd = datetime.datetime.now()
    changed = False
    diff = None
    out = ''

    rc, cmd, dumpout, err = get_config_key_dump(module)
    config_dump = json.loads(dumpout)
    current_value = get_config_key_current_value(option, config_dump)

    if state == 'present':
        if value == current_value:
            out = current_value or ''
        else:
            changed = True
            diff = dict(before=current_value, after=value)
            if not module.check_mode:
                rc, cmd, out, err = set_config_key_value(module, option, value)
                if rc:
                    fatal(message=f"Failed to set config-key '{option}'. Error:\n{err}", module=module)
            else:
                out = value
    else:
        # state == 'absent'
        if current_value is None:
            out = ''
        else:
            changed = True
            diff = dict(before=current_value, after='')
            if not module.check_mode:
                rc, cmd, out, err = del_config_key(module, option)
                if rc:
                    fatal(message=f"Failed to delete config-key '{option}'. Error:\n{err}", module=module)
            else:
                out = ''

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd,
                changed=changed, diff=diff)


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            option=dict(type='str', required=True),
            value=dict(type='str', required=False),
            state=dict(type='str', required=False, choices=['present', 'absent'], default='present'),
            fsid=dict(type='str', required=False),
            image=dict(type='str', required=False)
        ),
        supports_check_mode=True,
        required_if=[['state', 'present', ['value']]]
    )
    run(module)


if __name__ == '__main__':
    main()
