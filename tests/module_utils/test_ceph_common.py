import ceph_common
import pytest
from mock.mock import MagicMock


class TestCephCommon(object):
    def setup_method(self):
        self.fake_module = MagicMock()
        self.fake_params = {'foo': 'bar'}
        self.fake_module.params = self.fake_params

    def test_build_base_cmd_orch_with_fsid_arg(self):
        expected_cmd = ['cephadm', 'shell', '--fsid', '123', 'ceph', 'orch']
        self.fake_module.params = {'fsid': '123'}
        cmd = ceph_common.build_base_cmd_orch(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_orch_with_image_arg(self):
        expected_cmd = ['cephadm', '--image', 'quay.io/ceph-ci/ceph:main', 'shell', 'ceph', 'orch']
        self.fake_module.params = {'image': 'quay.io/ceph-ci/ceph:main'}
        cmd = ceph_common.build_base_cmd_orch(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_orch_with_docker_arg(self):
        expected_cmd = ['cephadm', '--docker', 'shell', 'ceph', 'orch']
        self.fake_module.params = {'docker': True}
        cmd = ceph_common.build_base_cmd_orch(self.fake_module)
        assert cmd == expected_cmd

    def test_build_base_cmd_orch_no_arg(self):
        expected_cmd = ['cephadm', 'shell', 'ceph', 'orch']
        cmd = ceph_common.build_base_cmd_orch(self.fake_module)
        assert cmd == expected_cmd

    def test_fatal(self):
        ceph_common.fatal("error", self.fake_module)
        self.fake_module.fail_json.assert_called_with(msg='error', rc=1)
        with pytest.raises(Exception):
            ceph_common.fatal("error", False)
