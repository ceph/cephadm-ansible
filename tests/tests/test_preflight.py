import pytest

class TestPreflight(object):
    @pytest.mark.no_client
    def test_cephadm_package_is_installed(self, node, host):
        assert host.package("cephadm").is_installed

    @pytest.mark.no_client
    def test_lvm2_package_is_installed(self, node, host):
        assert host.package("lvm2").is_installed

    def test_chrony_package_is_installed(self, node, host):
        assert host.package("chrony").is_installed

    @pytest.mark.no_client
    def test_podman_package_is_installed(self, node, host):
        assert host.package("podman").is_installed

    def test_chronyd_is_active(self, node, host):
        svc = host.service("chronyd")
        assert svc.is_enabled
        assert svc.is_running

    def test_cephcommon_package_is_installed(self, node, host):
        assert host.package("ceph-common").is_installed
