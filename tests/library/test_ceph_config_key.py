from __future__ import annotations

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
        assert res['diff'] == {'before': '10', 'after': '15'}
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
        assert res['stdout'] == '15'
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
        assert res['diff'] == {'before': '10', 'after': '15'}
        assert module.run_command.call_count == 1  # only dump
        assert res['stdout'] == '15'
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
        assert res['diff'] == {'before': '15', 'after': ''}
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
        assert res['diff'] == {'before': '15', 'after': ''}
        assert module.run_command.call_count == 1  # only dump
        assert res['stdout'] == ''
        assert res['rc'] == 0
