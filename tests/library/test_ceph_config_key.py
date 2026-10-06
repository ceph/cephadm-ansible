from typing import Any, Dict, Optional
from unittest.mock import MagicMock
import pytest
import common
import ceph_config_key


def _module_params(
    option: str,
    state: str = 'present',
    value: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        'option': option,
        'state': state,
        'fsid': None,
        'image': None,
    }
    if value is not None:
        params['value'] = value
    params.update(kwargs)
    return params


class TestCephConfigKey(object):

    def test_state_present_sets_config_key(self) -> None:
        """Test state=present sets config key when value differs."""
        module: MagicMock = MagicMock()
        module.params = _module_params(
            'config/mgr/mgr/prometheus/scrape_interval',
            state='present',
            value='15',
        )
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.side_effect = [
            (0, '{"config/mgr/mgr/prometheus/scrape_interval": "10"}', ''),  # dump
            (0, '', ''),  # set
        ]

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed'] is True
        assert res['cmd'] == [
            'cephadm', 'shell', 'ceph', 'config-key', 'set',
            'config/mgr/mgr/prometheus/scrape_interval', '-i', '-'
        ]
        assert res['diff'] == {'before': '', 'after': ''}
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0

    def test_state_present_idempotent(self) -> None:
        """Test state=present when value already matches (no change)."""
        module: MagicMock = MagicMock()
        module.params = _module_params(
            'config/mgr/mgr/prometheus/scrape_interval',
            state='present',
            value='15',
        )
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.return_value = (
            0,
            '{"config/mgr/mgr/prometheus/scrape_interval": "15"}',
            '',
        )

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert not res['changed']
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0

    def test_state_present_check_mode(self) -> None:
        """Test state=present in check mode (reports change, no set run)."""
        module: MagicMock = MagicMock()
        module.params = _module_params(
            'config/mgr/mgr/prometheus/scrape_interval',
            state='present',
            value='15',
        )
        module.check_mode = True
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.return_value = (
            0,
            '{"config/mgr/mgr/prometheus/scrape_interval": "10"}',
            '',
        )

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed']
        assert res['diff'] == {'before': '', 'after': ''}
        assert module.run_command.call_count == 1  # only dump
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0

    def test_state_absent_removes_config_key(self) -> None:
        """Test state=absent removes config key when it exists."""
        module: MagicMock = MagicMock()
        module.params = _module_params(
            'config/mgr/mgr/prometheus/scrape_interval',
            state='absent',
        )
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.side_effect = [
            (0, '{"config/mgr/mgr/prometheus/scrape_interval": "15"}', ''),  # dump
            (0, '', ''),  # del
        ]

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed'] is True
        assert res['cmd'] == [
            'cephadm', 'shell', 'ceph', 'config-key', 'del',
            'config/mgr/mgr/prometheus/scrape_interval',
        ]
        assert res['diff'] == {'before': '', 'after': ''}
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0

    def test_state_absent_idempotent(self) -> None:
        """Test state=absent when key does not exist (no change)."""
        module: MagicMock = MagicMock()
        module.params = _module_params('nonexistent/key', state='absent')
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.return_value = (0, '{}', '')

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert not res['changed']
        assert res['stdout'] == ''
        assert res['rc'] == 0
        assert module.run_command.call_count == 1  # only dump, no del

    def test_state_absent_check_mode(self) -> None:
        """Test state=absent in check mode (reports change, no del run)."""
        module: MagicMock = MagicMock()
        module.params = _module_params(
            'config/mgr/mgr/prometheus/scrape_interval',
            state='absent',
        )
        module.check_mode = True
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.return_value = (
            0,
            '{"config/mgr/mgr/prometheus/scrape_interval": "15"}',
            '',
        )

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed']
        assert res['diff'] == {'before': '', 'after': ''}
        assert module.run_command.call_count == 1  # only dump
        assert res['stdout'] == ''
        assert res['rc'] == 0

    def test_state_present_different_secret_values_not_exposed_in_output(self) -> None:
        """Test state=present with differing old and new secrets does not expose secrets in result."""
        old_secret = 'old-secret-password-123'
        new_secret = 'new-secret-password-456'
        option = 'config/mgr/mgr/dashboard/jwt_secret'

        module: MagicMock = MagicMock()
        module.params = _module_params(
            option,
            state='present',
            value=new_secret,
        )
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.side_effect = [
            (0, f'{{"{option}": "{old_secret}"}}', ''),  # dump
            (0, '', ''),  # set
        ]

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed'] is True
        assert res['diff'] == {'before': '', 'after': ''}
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0
        assert old_secret not in str(res)
        assert new_secret not in str(res)

    def test_state_absent_without_value_secret_not_exposed_in_output(self) -> None:
        """Test state=absent without supplying a value does not expose existing secret in result."""
        old_secret = 'super-confidential-secret-789'
        option = 'config/mgr/mgr/dashboard/jwt_secret'

        module: MagicMock = MagicMock()
        module.params = _module_params(
            option,
            state='absent',
        )
        assert 'value' not in module.params
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json

        module.run_command.side_effect = [
            (0, f'{{"{option}": "{old_secret}"}}', ''),  # dump
            (0, '', ''),  # del
        ]

        with pytest.raises(common.AnsibleExitJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert res['changed'] is True
        assert res['cmd'] == [
            'cephadm', 'shell', 'ceph', 'config-key', 'del',
            option,
        ]
        assert res['diff'] == {'before': '', 'after': ''}
        assert res['stdout'] == ''
        assert res['stderr'] == ''
        assert res['rc'] == 0
        assert old_secret not in str(res)

    def test_failure_dump_does_not_leak_raw_stderr(self) -> None:
        """Test dump failure does not leak stderr containing sensitive info."""
        module: MagicMock = MagicMock()
        module.params = _module_params('some/key', state='present', value='val')
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json
        module.run_command.return_value = (1, '', 'sensitive debug trace')

        with pytest.raises(common.AnsibleFailJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert 'sensitive debug trace' not in res['msg']
        assert res['msg'] == "Can't get current configuration via `ceph config-key dump`."

    def test_failure_set_does_not_leak_raw_stderr(self) -> None:
        """Test set failure does not leak stderr containing sensitive info."""
        module: MagicMock = MagicMock()
        module.params = _module_params('config/mgr/secret', state='present', value='new_val')
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json
        module.run_command.side_effect = [
            (0, '{"config/mgr/secret": "old_val"}', ''),  # dump
            (1, '', 'sensitive stderr output'),  # set fails
        ]

        with pytest.raises(common.AnsibleFailJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert 'sensitive stderr output' not in res['msg']
        assert res['msg'] == "Failed to set config-key 'config/mgr/secret'."

    def test_failure_del_does_not_leak_raw_stderr(self) -> None:
        """Test del failure does not leak stderr containing sensitive info."""
        module: MagicMock = MagicMock()
        module.params = _module_params('config/mgr/secret', state='absent')
        module.check_mode = False
        module.exit_json.side_effect = common.exit_json
        module.fail_json.side_effect = common.fail_json
        module.run_command.side_effect = [
            (0, '{"config/mgr/secret": "old_val"}', ''),  # dump
            (1, '', 'sensitive stderr output'),  # del fails
        ]

        with pytest.raises(common.AnsibleFailJson) as result:
            ceph_config_key.run(module)

        res: Dict[str, Any] = result.value.args[0]
        assert 'sensitive stderr output' not in res['msg']
        assert res['msg'] == "Failed to delete config-key 'config/mgr/secret'."
