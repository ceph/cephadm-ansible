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
from typing import TYPE_CHECKING, List, Tuple
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule  # type: ignore
try:
    from ansible.module_utils.ceph_common import exit_module  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module
import datetime


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_orch_apply
short_description: apply service spec
version_added: "2.9"
description:
    - apply a service spec
options:
    name:
        description:
            - name of the host
        required: true
    address:
        description:
            - address of the host
        required: true when state is present
    set_admin_label:
        description:
            - enforce '_admin' label on the host specified
              in 'name'
        required: false
        default: false
    labels:
        description:
            - list of labels to apply on the host
        required: false
        default: []
    state:
        description:
            - if set to 'present', it will ensure the name specified
              in 'name' will be present.
            - if set to 'present', it will remove the host specified in
              'name'.
            - if set to 'drain', it will schedule to remove all daemons
              from the host specified in 'name'.
        required: false
        default: present
author:
    - Guillaume Abrioux <gabrioux@redhat.com>
'''

EXAMPLES = '''
- name: apply osd spec
    ceph_orch_apply:
    spec: |
        service_type: osd
        service_id: osd
        placement:
        label: osds
        spec:
        data_devices:
            all: true
'''


def build_base_cmd(module: "AnsibleModule") -> List[str]:
    cmd = ['cephadm']
    if module.params.get('docker'):
        cmd.append('--docker')
    cmd.extend(['shell', 'ceph', 'orch'])
    return cmd


def apply_spec(module: "AnsibleModule",
               data: str) -> Tuple[int, List[str], str, str]:
    cmd = build_base_cmd(module)
    cmd.extend(['apply', '-i', '-'])
    rc, out, err = module.run_command(cmd, data=data)

    if rc:
        raise RuntimeError(err)

    return rc, cmd, out, err


def main():
    module = AnsibleModule(
        argument_spec=dict(
            spec=dict(type='str', required=True),
            docker=dict(type=bool,
                        required=False,
                        default=False)
        ),
    )

    spec = module.params.get('spec')

    startd = datetime.datetime.now()
    changed = False

    rc, cmd, out, err = apply_spec(module, spec)
    changed = True

    if module.check_mode:
        exit_module(
            module=module,
            out='',
            rc=0,
            cmd=cmd,
            err='',
            startd=startd,
            changed=False
        )
    else:
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
