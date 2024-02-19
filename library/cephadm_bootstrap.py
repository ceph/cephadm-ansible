#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Red Hat
# SPDX-License-Identifier: Apache-2.0
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
try:
    from ansible.module_utils.ceph_common import exit_module  # type: ignore
except ImportError:
    from module_utils.ceph_common import exit_module
import datetime
import os

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: cephadm_bootstrap
short_description: Bootstrap a Ceph cluster via cephadm
version_added: "2.8"
description:
    - Bootstrap a Ceph cluster via cephadm
options:
    mon_ip:
        description:
            - Ceph monitor IP address.
        required: true
    image:
        description:
            - Ceph container image.
        required: false
    docker:
        description:
            - Use docker instead of podman.
        required: false
    fsid:
        description:
            - Ceph FSID.
        required: false
    pull:
        description:
            - Pull the Ceph container image.
        required: false
        default: true
    dashboard:
        description:
            - Deploy the Ceph dashboard.
        required: false
        default: true
    dashboard_user:
        description:
            - Ceph dashboard user.
        required: false
    dashboard_password:
        description:
            - Ceph dashboard password.
        required: false
    monitoring:
        description:
            - Deploy the monitoring stack.
        required: false
        default: true
    firewalld:
        description:
            - Manage firewall rules with firewalld.
        required: false
        default: true
    allow_overwrite:
        description:
            - allow overwrite of existing –output-* config/keyring/ssh files.
        required: false
        default: false
    registry_url:
        description:
            - URL for custom registry.
        required: false
    registry_username:
        description:
            - Username for custom registry.
        required: false
    registry_password:
        description:
            - Password for custom registry.
        required: false
    registry_json:
        description:
            - JSON file with custom registry login info (URL,
              username, password).
        required: false
    ssh_user:
        description:
            - SSH user used for cephadm ssh to the hosts.
        required: false
    ssh_config:
        description:
            - SSH config file path for cephadm ssh client.
        required: false
    allow_fqdn_hostname:
        description:
            - Allow hostname that is fully-qualified.
        required: false
        default: false
    cluster_network:
        description:
            - subnet to use for cluster replication, recovery and heartbeats.
        required: false
author:
    - Dimitri Savineau <dsavinea@redhat.com>
    - Teoman ONAY <tonay@ibm.com>
'''

EXAMPLES = '''
- name: bootstrap a cluster via cephadm (with default values)
  cephadm_bootstrap:
    mon_ip: 192.168.42.1

- name: bootstrap a cluster via cephadm (with custom values)
  cephadm_bootstrap:
    mon_ip: 192.168.42.1
    fsid: 3c9ba63a-c7df-4476-a1e7-317dfc711f82
    image: quay.ceph.io/ceph/daemon-base:latest-main-devel
    dashboard: false
    monitoring: false
    firewalld: false

- name: bootstrap a cluster via cephadm with custom image via env var
  cephadm_bootstrap:
    mon_ip: 192.168.42.1
  environment:
    CEPHADM_IMAGE: quay.ceph.io/ceph/daemon-base:latest-main-devel
'''

RETURN = '''#  '''


def run_module() -> None:

    backward_compat = dict(
        dashboard=dict(type='bool', required=False, remove_in_version='4.0.0'),
        firewalld=dict(type='bool', required=False, remove_in_version='4.0.0'),
        monitoring=dict(type='bool',
                        required=False,
                        remove_in_version='4.0.0'),
        pull=dict(type='bool', required=False, remove_in_version='4.0.0'),
        dashboard_password=dict(type='str',
                                required=False,
                                no_log=True),
        dashboard_user=dict(type='str', required=False),
    )

    cephadm_params = dict(
        docker=dict(type='bool', required=False, default=False),
        image=dict(type='str', required=False),
    )

    cephadm_bootstrap_downstream_only = dict(
        call_home_config=dict(type='str', required=False),
        call_home_icn=dict(type='str', required=False),
        ceph_call_home_contact_email=dict(type='str', required=False),
        ceph_call_home_contact_first_name=dict(type='str', required=False),
        ceph_call_home_contact_last_name=dict(type='str', required=False),
        ceph_call_home_contact_phone=dict(type='str', required=False),
        ceph_call_home_country_code=dict(type='str', required=False),
        deploy_cephadm_agent=dict(type='bool', required=False),
        enable_ibm_call_home=dict(type='bool', required=False),
        enable_storage_insights=dict(type='bool', required=False),
        storage_insights_config=dict(type='str', required=False),
        storage_insights_tenant_id=dict(type='str', required=False),
    )

    cephadm_bootstrap_params = dict(
        allow_fqdn_hostname=dict(type='bool', required=False, default=False),
        allow_mismatched_release=dict(type='bool', required=False),
        allow_overwrite=dict(type='bool', required=False, default=False),
        apply_spec=dict(type='str', required=False),
        cluster_network=dict(type='str', required=False),
        config=dict(type='str', required=False),
        dashboard_crt=dict(type='str', required=False),
        dashboard_key=dict(type='str', required=False),
        dashboard_password_noupdate=dict(type='bool', required=False),
        fsid=dict(type='str', required=False),
        initial_dashboard_password=dict(type='str',
                                        required=False,
                                        no_log=True),
        initial_dashboard_user=dict(type='str', required=False),
        log_to_file=dict(type='bool', required=False),
        mgr_id=dict(type='str', required=False),
        mon_addrv=dict(type='str', required=False),
        mon_id=dict(type='str', required=False),
        mon_ip=dict(type='str', required=False),
        no_cleanup_on_failure=dict(type='bool', required=False),
        no_minimize_config=dict(type='bool', required=False),
        orphan_initial_daemons=dict(type='bool', required=False),
        output_config=dict(type='str', required=False),
        output_dir=dict(type='str', required=False),
        output_keyring=dict(type='str', required=False),
        output_pub_ssh_key=dict(type='str', required=False),
        registry_json=dict(type='str', required=False),
        registry_password=dict(type='str', required=False, no_log=True),
        registry_url=dict(type='str', required=False),
        registry_username=dict(type='str', required=False),
        shared_ceph_folder=dict(type='str', required=False),
        single_host_defaults=dict(type='bool', required=False),
        skip_admin_label=dict(type='bool', required=False),
        skip_dashboard=dict(type='bool', required=False, default=False),
        skip_firewalld=dict(type='bool', required=False, default=False),
        skip_monitoring_stack=dict(type='bool', required=False, default=False),
        skip_mon_network=dict(type='bool', required=False),
        skip_ping_check=dict(type='bool', required=False),
        skip_prepare_host=dict(type='bool', required=False),
        skip_pull=dict(type='bool', required=False),
        skip_ssh=dict(type='bool', required=False),
        ssh_config=dict(type='str', required=False),
        ssh_private_key=dict(type='str', required=False),
        ssh_public_key=dict(type='str', required=False),
        ssh_signed_cert=dict(type='str', required=False),
        ssh_user=dict(type='str', required=False),
        ssl_dashboard_port=dict(type='str', required=False),
        with_centralized_logging=dict(type='bool', required=False),
        **cephadm_bootstrap_downstream_only,
    )

    module = AnsibleModule(
        argument_spec={**cephadm_params,
                       **cephadm_bootstrap_params,
                       **backward_compat},
        supports_check_mode=True,
        mutually_exclusive=[
            ('registry_json', 'registry_url'),
            ('registry_json', 'registry_username'),
            ('registry_json', 'registry_password'),
            ('mon_addrv', 'mon_ip'),
        ],
        required_together=[
            ('registry_url', 'registry_username', 'registry_password'),
            ('initial_dashboard_user', 'initial_dashboard_password'),
        ],
        required_one_of=[('mon_ip', 'mon_addrv'),
                         ],
    )

    fsid = module.params.get('fsid')
    allow_overwrite = module.params.get('allow_overwrite')

    startd = datetime.datetime.now()

    cmd: list[str] = []
    data_dir = '/var/lib/ceph'
    ceph_conf = 'ceph.conf'
    ceph_keyring = 'ceph.client.admin.keyring'
    ceph_pubkey = 'ceph.pub'

    def extend_append(command: str, params: dict) -> list:
        cmd: list[str] = []
        cmd.append(command)
        for k in params:
            if module.params.get(k):
                if params[k]['type'] == 'bool':
                    cmd.append('--' + k.replace('_', '-'))
                else:
                    cmd.extend(['--' + k.replace('_', '-'),
                                module.params.get(k)])
        return cmd

    if fsid:
        if os.path.exists(os.path.join(data_dir, fsid)):
            out = f'A cluster with fsid {fsid} is already deployed.'
            exit_module(
                rc=0,
                startd=startd,
                module=module,
                cmd=cmd,
                out=out,
                changed=False
            )

    for f in [ceph_conf,
              ceph_keyring,
              ceph_pubkey]:
        if not allow_overwrite:
            path: str = os.path.join(data_dir, f)
            if os.path.exists(path):
                out = f'{path} already exists, skipping.'
                exit_module(
                    rc=0,
                    startd=startd,
                    module=module,
                    cmd=cmd,
                    out=out,
                    changed=False
                )

    # Build cephadm with parameters
    cmd = extend_append('cephadm', cephadm_params)
    # Extends with boostrap parameters
    cmd.extend(extend_append('bootstrap', cephadm_bootstrap_params))

    # keep backward compatibility
    for k in backward_compat:
        result = module.params.get(k)
        if result is not None:
            if k == 'pull' and not result:
                if '--skip-pull' not in cmd:
                    cmd.append('--skip-pull')
            elif k == 'monitoring' and not result:
                if '--skip-monitoring-stack' not in cmd:
                    cmd.append('--skip-monitoring-stack')
            elif k == 'firewalld' and not result:
                if '--skip-firewalld' not in cmd:
                    cmd.append('--skip-firewalld')
            elif k == 'dashboard':
                if result:
                    if 'dashboard-user' not in cmd:
                        cmd.extend(['--dashboard-user',
                                    module.params.get('dashboard_user'),
                                    '--dashboard-password',
                                    module.params.get('dashboard_password'),
                                    ])
                else:
                    if '--skip-dashboard' not in cmd:
                        cmd.append('--skip-dashboard')

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
        rc, out, err = module.run_command(cmd)
        exit_module(
            module=module,
            out=out,
            rc=rc,
            cmd=cmd,
            err=err,
            startd=startd,
            changed=True
        )


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
