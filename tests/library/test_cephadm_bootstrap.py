import pytest
from unittest.mock import patch, MagicMock
import cephadm_bootstrap
import common

fake_ip = '10.0.0.1'
fake_image = 'quay.ceph.io/ceph/daemon-base:latest'
fake_fsid = '3c9ba63a-c7df-4476-a1e7-317dfc711f82'
fake_registry = 'quay.io'
fake_registry_user = 'user'
fake_registry_pass = 'pass'
fake_registry_json = '/tmp/registry.json'


class TestCephadmBootstrapModule:
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_docker(self, m_run_command, m_exit_json):
        module = MagicMock()
        module.params = {'mon_ip': fake_ip, 'docker': True}
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        m_run_command.return_value = 0, '', ''
        module.run_command = m_run_command

        cephadm_params = dict(docker=dict(type='bool', required=False),
                              image=dict(type='str', required=False))
        cephadm_bootstrap_params = dict(mon_ip=dict(type='str', required=False))
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params, cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert res['changed']
        assert '--docker' in res['cmd']
        assert '--mon-ip' in res['cmd']
        assert res['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_custom_image(self, m_run_command, m_exit_json):
        module = MagicMock()
        module.params = {'mon_ip': fake_ip, 'image': fake_image}
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        m_run_command.return_value = 0, '', ''
        module.run_command = m_run_command

        cephadm_params = dict(docker=dict(type='bool', required=False),
                              image=dict(type='str', required=False))
        cephadm_bootstrap_params = dict(mon_ip=dict(type='str', required=False))
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params, cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert res['changed']
        assert '--image' in res['cmd']
        assert fake_image in res['cmd']
        assert '--mon-ip' in res['cmd']
        assert res['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_check_mode(self, m_run_command):
        module = MagicMock()
        module.params = {'mon_ip': fake_ip}
        module.check_mode = True
        module.exit_json.side_effect = common.exit_json
        module.run_command = m_run_command
        m_run_command.return_value = (0, '', '')

        cephadm_params = {}
        cephadm_bootstrap_params = {'mon_ip': {'type': 'str'}}
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params, cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert not res['changed']
        assert '--mon-ip' in res['cmd']
        assert res['rc'] == 0
        assert res['stdout'] == ''
        assert res['stderr'] == ''

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_failure(self, m_run_command):
        module = MagicMock()
        module.params = {'mon_ip': fake_ip}
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.run_command = m_run_command
        m_run_command.return_value = (1, '', 'ERROR: cephadm should be run as root')

        cephadm_params = {}
        cephadm_bootstrap_params = {'mon_ip': {'type': 'str'}}
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params, cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert res['changed']
        assert '--mon-ip' in res['cmd']
        assert res['rc'] == 1
        assert res['stderr'] == 'ERROR: cephadm should be run as root'

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_default_values(self, m_run_command):
        module = MagicMock()
        module.params = {'mon_ip': fake_ip}
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.run_command = m_run_command
        m_run_command.return_value = (0, 'Bootstrap complete.', '')

        cephadm_params = {}
        cephadm_bootstrap_params = {'mon_ip': {'type': 'str'}}
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params, cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert res['changed']
        assert '--mon-ip' in res['cmd']
        assert res['rc'] == 0
        assert res['stdout'] == 'Bootstrap complete.'
        assert res['stderr'] == ''

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_with_license_and_disable_call_home(self, m_run_command):
        module = MagicMock()
        module.params = {
            'mon_ip': fake_ip,
            'automatically_accept_license': True,
            'disable_ibm_call_home': True,
        }
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.run_command = m_run_command
        m_run_command.return_value = (0, 'Bootstrap complete.', '')

        cephadm_params = {}
        cephadm_bootstrap_params = {
            'mon_ip': {'type': 'str'},
            'automatically_accept_license': {'type': 'bool'},
            'disable_ibm_call_home': {'type': 'bool'},
        }
        backward_compat = {}

        with pytest.raises(common.AnsibleExitJson) as result:
            cephadm_bootstrap.run(module, cephadm_params,
                                  cephadm_bootstrap_params, backward_compat)

        res = result.value.args[0]
        assert res['changed']
        assert '--mon-ip' in res['cmd']
        assert '--automatically-accept-license' in res['cmd']
        assert '--disable-ibm-call-home' in res['cmd']
        assert res['rc'] == 0
