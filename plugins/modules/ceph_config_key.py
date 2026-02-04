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
short_description: get/set ceph config-key
version_added: ""
description:
    - Set Ceph config key options.
options:
    fsid:
        type: str
        description:
            - the fsid of the Ceph cluster to interact with.
        required: false
    image:
        type: str
        description:
            - The Ceph container image to use.
        required: false
    action:
        type: str
        description:
            - whether to get or set the parameter specified in 'option'
        required: false
        default: 'set'
    option:
        type: str
        description:
            - name of the parameter to be set
        required: true
    value:
        type: str
        description:
            - value of the parameter
        required: true if action is 'set'

'''

EXAMPLES = '''
- name: get config/mgr/mgr/prometheus/scrape_interval
  ceph_config_key:
    action: get
    option: config/mgr/mgr/prometheus/scrape_interval

- name: set config/mgr/mgr/prometheus/scrape_interval to 15s
  ceph_config_key:
    action: set
    option: config/mgr/mgr/prometheus/scrape_interval
    value: 15

- name: set mgr/cephadm/services/prometheus/prometheus.yml from file
  ceph_config_key:
    action: set
    option: mgr/cephadm/services/prometheus/prometheus.yml
    value: '{{lookup("file","/path/to/prometheus.yml")}}'
'''

RETURN = '''#  '''


def set_config_key_value(module: "AnsibleModule",
                         option: str,
                         value: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'config-key', 'set', option, '-i', '-'])

    # pass the value through stdin to avoid issues with multi-line values, encoding, etc.
    rc, out, err = module.run_command(args=cmd, data=value)

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
            return config_dump[key]
    return None


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(type='str', required=False, choices=['get', 'set'], default='set'),
            option=dict(type='str', required=False),
            value=dict(type='str', required=False),
            fsid=dict(type='str', required=False),
            image=dict(type='str', required=False)
        ),
        supports_check_mode=True,
        required_if=[['action', 'set', ['value']]]
    )

    # Gather module parameters in variables
    option = module.params.get('option')
    value = module.params.get('value')
    action = module.params.get('action')

    startd = datetime.datetime.now()
    changed = False

    # getting the value via a dump simplifies checking whether the value is currently set
    rc, cmd, dumpout, err = get_config_key_dump(module)
    config_dump = json.loads(dumpout)
    current_value = get_config_key_current_value(option, config_dump)
    diff = None
    out = ''

    if action == 'set':
        if value is None:
            module.fail_json(msg="Value is required when action is set")
        elif value == current_value:
            out = 'option={} already set. Skipping.'.format(option)
        else:
            changed = True
            diff = dict(before=current_value, after=value)
            if not module.check_mode:
                rc, cmd, out, err = set_config_key_value(module, option, value)
    else:
        if current_value is None:
            out = ''
            err = 'No value found for option={}'.format(option)
        else:
            out = current_value

    exit_module(module=module, out=out, rc=rc,
                cmd=cmd, err=err, startd=startd,
                changed=changed, diff=diff)


if __name__ == '__main__':
    main()
