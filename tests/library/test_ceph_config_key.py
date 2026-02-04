from mock.mock import patch
import pytest
import common
import ceph_config_key


class TestCephConfigKey(object):

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_set_config_key(self, m_run_command, m_exit_json):
        """
        Test setting a config key value
        """
        common.set_module_args({
            'action': 'set',
            'option': 'config/mgr/mgr/prometheus/scrape_interval',
            'value': '15'
        })
        m_exit_json.side_effect = common.exit_json

        # Mock the config-key dump response
        m_run_command.side_effect = [
            (0, '{"config/mgr/mgr/prometheus/scrape_interval": "10"}', ''),  # dump response
            (0, '', '')  # set response
        ]

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert result['changed'] is True
        assert result['cmd'] == ['cephadm',
                                 'shell',
                                 'ceph',
                                 'config-key',
                                 'set',
                                 'config/mgr/mgr/prometheus/scrape_interval',
                                 '-i',
                                 '-']
        assert result['diff'] == {'before': '10', 'after': '15'}
        assert result['stdout'] == ''
        assert result['stderr'] == ''
        assert result['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_set_config_key_idempotent(self, m_run_command, m_exit_json):
        """
        Test setting a config key value that's already set
        """
        common.set_module_args({
            'action': 'set',
            'option': 'config/mgr/mgr/prometheus/scrape_interval',
            'value': '15'
        })
        m_exit_json.side_effect = common.exit_json

        # Mock the config-key dump response
        m_run_command.return_value = (0, '{"config/mgr/mgr/prometheus/scrape_interval": "15"}', '')

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['stdout'] == 'option=config/mgr/mgr/prometheus/scrape_interval already set. Skipping.'
        assert result['stderr'] == ''
        assert result['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_get_config_key(self, m_run_command, m_exit_json):
        """
        Test getting a config key value
        """
        common.set_module_args({
            'action': 'get',
            'option': 'config/mgr/mgr/prometheus/scrape_interval'
        })
        m_exit_json.side_effect = common.exit_json

        # Mock the config-key dump response
        m_run_command.return_value = (0, '{"config/mgr/mgr/prometheus/scrape_interval": "15"}', '')

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['stdout'] == '15'
        assert result['stderr'] == ''
        assert result['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_get_config_key_nonexistent(self, m_run_command, m_exit_json):
        """
        Test getting a config key that doesn't exist
        """
        common.set_module_args({
            'action': 'get',
            'option': 'nonexistent/key'
        })
        m_exit_json.side_effect = common.exit_json

        # Mock the config-key dump response
        m_run_command.return_value = (0, '{}', '')

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['stdout'] == ''
        assert result['stderr'] == 'No value found for option=nonexistent/key'
        assert result['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_set_config_key_check_mode(self, m_run_command, m_exit_json):
        """
        Test setting a config key in check mode
        """
        common.set_module_args({
            'action': 'set',
            'option': 'config/mgr/mgr/prometheus/scrape_interval',
            'value': '15',
            '_ansible_check_mode': True
        })
        m_exit_json.side_effect = common.exit_json

        # Mock the config-key dump response
        m_run_command.return_value = (0, '{"config/mgr/mgr/prometheus/scrape_interval": "10"}', '')

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['diff'] == {'before': '10', 'after': '15'}
        # Verify no set command was actually run
        assert m_run_command.call_count == 1  # only the dump command was called
        assert result['stdout'] == ''
        assert result['stderr'] == ''
        assert result['rc'] == 0

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    def test_set_config_key_missing_value(self, m_fail_json):
        """
        Test setting a config key without providing a value
        """
        common.set_module_args({
            'action': 'set',
            'option': 'config/mgr/mgr/prometheus/scrape_interval'
        })
        m_fail_json.side_effect = common.fail_json

        with pytest.raises(common.AnsibleFailJson) as result:
            ceph_config_key.main()

        result = result.value.args[0]
        assert result['msg'] == 'action is set but all of the following are missing: value'
