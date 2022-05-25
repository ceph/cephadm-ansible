import ceph_common
import pytest
from mock.mock import MagicMock


class TestCephCommon(object):
    def setup_method(self):
        self.fake_module = MagicMock()
        self.fake_params = {}
        self.fake_module.params = self.fake_params

    def test_build_base_cmd_sh_with_fsid(self):
        expected_cmd = ['cephadm', 'shell', '--fsid', '123']
        self.fake_module.params = {'fsid': '123'}
        cmd = ceph_common.build_base_cmd_sh(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_sh_no_arg(self):
        expected_cmd = ['cephadm', 'shell']
        cmd = ceph_common.build_base_cmd_sh(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_no_arg(self):
        expected_cmd = ['cephadm', 'shell', 'ceph', 'orch']
        cmd = ceph_common.build_base_cmd(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_with_docker_arg(self):
        expected_cmd = ['cephadm', '--docker', 'shell', 'ceph', 'orch']
        self.fake_module.params = {'docker': True}
        cmd = ceph_common.build_base_cmd(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_with_fsid_arg(self):
        expected_cmd = ['cephadm', 'shell', '--fsid', '456', 'ceph', 'orch']
        self.fake_module.params = {'fsid': '456'}
        cmd = ceph_common.build_base_cmd(self.fake_module)
        assert cmd == expected_cmd

    def test_fatal(self):
        ceph_common.fatal("error", self.fake_module)
        self.fake_module.fail_json.assert_called_with(msg='error', rc=1)
        with pytest.raises(Exception):
            ceph_common.fatal("error", False)
