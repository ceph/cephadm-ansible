# Copyright Red Hat
# SPDX-License-Identifier: Apache-2.0
# Author: Guillaume Abrioux <gabrioux@redhat.com>
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
from typing import List, Tuple
try:
    from ansible.module_utils.ceph_common import exit_module, build_base_cmd, fatal  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module, build_base_cmd, fatal
import datetime

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: cephadm_registry_login
short_description: Log in to container registry
version_added: "2.9"
description:
    - Call cephadm registry-login command for logging in to container registry
options:
    state:
        description:
            - log in or log out from the registry.
        default: login
        required: false
    docker:
        description:
            - Use docker instead of podman.
        required: false
    registry_url:
        description:
            - The url of the registry
        required: true
    registry_username:
        description:
            - The username to log in
        required: true when state is 'login'
    registry_password:
        description:
            - The corresponding password to log in.
        required: true when state is 'login'
    registry_json:
        description:
            - The path to a json file. This file must be present on remote hosts
              prior to running this task.
              *not supported yet*.
author:
    - Guillaume Abrioux <gabrioux@redhat.com>
'''

EXAMPLES = '''
- name: log in to quay.io registry
  cephadm_registry_login:
    registry_url: quay.io
    registry_username: my_login
    registry_password: my_password

- name: log out from quay.io registry
  cephadm_registry_login:
    state: logout
    registry_url: quay.io
'''

RETURN = '''#  '''


def build_base_container_cmd(module: "AnsibleModule", action: str = 'login') -> List[str]:
    docker = module.params.get('docker')
    container_binary = 'podman'

    if docker:
        container_binary = 'docker'

    cmd = [container_binary, action]

    return cmd


def is_logged(module: "AnsibleModule") -> bool:
    registry_url = module.params.get('registry_url')
    registry_username = module.params.get('registry_username')
    cmd = build_base_container_cmd(module)

    cmd.extend(['--get-login', registry_url])

    rc, out, err = module.run_command(cmd)

    if not rc and out.strip() == registry_username:
        return True

    return False


def do_login_or_logout(module: "AnsibleModule", action: str = 'login') -> Tuple[int, List[str], str, str]:
    registry_url = module.params.get('registry_url')
    registry_username = module.params.get('registry_username')
    registry_password = module.params.get('registry_password')

    cmd = build_base_container_cmd(module, action)
    if action == 'login':
        cmd.extend(['--username', registry_username, '--password-stdin', registry_url])
    else:
        cmd.extend([registry_url])

    rc, out, err = module.run_command(cmd, data=registry_password)

    return rc, cmd, out, err


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', required=False, default='login', choices=['login', 'logout']),
            docker=dict(type=bool,
                        required=False,
                        default=False),
            registry_url=dict(type='str', required=True),
            registry_username=dict(type='str', required=False),
            registry_password=dict(type='str', required=False, no_log=True),
            registry_json=dict(type='str', required=False)
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ('registry_json', 'registry_url'),
            ('registry_json', 'registry_username'),
            ('registry_json', 'registry_password'),
        ],
        # Note: the following might be needed when registry_json will be implemented
        # required_together=[
        #     ('registry_url', 'registry_username', 'registry_password')
        # ],
        required_if=[
            ['state', 'login', ['registry_username', 'registry_password']],
            ['state', 'logout', ['registry_url']]
        ]
    )
    startd = datetime.datetime.now()
    changed = False
    cmd = build_base_cmd(module)
    cmd.append('registry-login')

    state = module.params.get('state')
    registry_url = module.params.get('registry_url')
    registry_username = module.params.get('registry_username')
    registry_json = module.params.get('registry_json')

    if module.check_mode:
        exit_module(
            module=module,
            out='',
            rc=0,
            cmd=[],
            err='',
            startd=startd,
            changed=False
        )
    if registry_json:
        fatal('This feature is not supported yet.', module)
    current_status = is_logged(module)
    action = None
    skip_msg = {
        'login': f'Already logged in to {registry_url} with {registry_username}.',
        'logout': f'Already logged out from {registry_url}.'
    }
    action_msg = {
         'login': f'Couldn\'t log in to {registry_url} with {registry_username}.',
         'logout': f'Couldn\'t log out from {registry_url}.'
    }

    if state == 'login' and not current_status or state == 'logout' and current_status:
        action = state
    else:
        out = skip_msg[state]
        rc = 0
        err = ''
        cmd = []

    if action:
        rc, cmd, out, err = do_login_or_logout(module, action)
        if rc:
            msg = f'{action_msg[state]}\nCmd: {cmd}\nErr: {err}'
            fatal(msg, module)
        else:
            changed = True

    exit_module(
        module=module,
        out=out,
        rc=rc,
        cmd=cmd,
        err=err,
        startd=startd,
        changed=changed
    )


if __name__ == '__main__':
    main()
