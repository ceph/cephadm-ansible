from mock.mock import patch
import pytest
import common
import ceph_orch_host


class TestCephOrchHost(object):

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_absent_host_exists(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'absent',
            'name': 'ceph-node5'
        })
        m_exit_json.side_effect = common.exit_json
        stdout = "Removed  host 'ceph-node5'"
        stderr = ''
        rc = 0
        m_run_command.return_value = rc, stdout, stderr
        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_orch_host.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == ["cephadm", "shell", "ceph", "orch", "host", "rm", "ceph-node5"]
        assert result['stdout'] == stdout
        assert result['rc'] == 0

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_absent_host_doesnt_exist(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'absent',
            'name': 'ceph-node1'
        })
        m_exit_json.side_effect = common.exit_json

        stdout = ""
        stderr = "Error EINVAL: host ceph-node1 does not exist"
        rc = 0
        m_run_command.return_value = rc, stdout, stderr

        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_orch_host.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['stdout'] == 'ceph-node1 is not present, skipping.'
        assert result['rc'] == 0

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_drain(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'drain',
            'name': 'ceph-node5'
        })
        m_exit_json.side_effect = common.exit_json
        stdout = """
Scheduled to remove the following daemons from host 'ceph-node5'
type                 id
-------------------- ---------------
crash                ceph-node5
osd                  3
osd                  5
osd                  7"""
        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        stderr = ''
        rc = 0
        cmd = ["cephadm", "shell", "ceph", "orch", "host", "drain", "ceph-node5"]
        m_run_command.return_value = rc, stdout, stderr
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_orch_host.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == cmd
        assert result['stdout'] == stdout
        assert result['rc'] == 0

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_present_no_label_diff(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'present',
            'name': 'ceph-node5'
        })
        m_exit_json.side_effect = common.exit_json
        stdout = "ceph-node5 is already present, skipping."
        stderr = ''
        rc = 0
        m_run_command.return_value = rc, stdout, stderr
        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_orch_host.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['stdout'] == stdout
        assert result['rc'] == 0

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_present_label_diff(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'present',
            'name': 'ceph-node5',
            'labels': ["label1", "label2"]
        })
        m_exit_json.side_effect = common.exit_json
        stdout = "Label(s) updated:"
        stderr = ''
        rc = 0
        m_run_command.side_effect = [(rc, "Added label label1 to host ceph-node5", stderr),
                                     (rc, "Added label label2 to host ceph-node5", stderr)]
        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_orch_host.main()

        result = result.value.args[0]
        assert result['changed']
        assert stdout in result['stdout']
        assert 'label1' in result['stdout']
        assert 'label2' in result['stdout']
        assert result['rc'] == 0

    @patch('ceph_orch_host.get_current_state')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_state_present_label_diff_error(self, m_run_command, m_exit_json, m_get_current_state):
        common.set_module_args({
            'state': 'present',
            'name': 'ceph-node5',
            'labels': ["label1", "label2"]
        })
        m_exit_json.side_effect = common.exit_json
        stdout = ''
        stderr = 'fake error'
        rc = 0
        m_run_command.return_value = 1, stdout, stderr
        m_get_current_state_stdout = '[{"addr": "10.10.10.11", "hostname": "ceph-node5", "labels": [], "status": ""}]'
        m_get_current_state.return_value = rc, ["cephadm",
                                                "shell",
                                                "ceph",
                                                "orch",
                                                "host",
                                                "ls",
                                                "--format",
                                                "json"], m_get_current_state_stdout, stderr

        with pytest.raises(RuntimeError) as result:
            ceph_orch_host.main()
            assert result == 'fake error'
