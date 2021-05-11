class TestPreflight(object):
    def test_cephadm_package_is_installed(self, host):
        assert host.package("cephadm").is_installed

    def test_lvm2_package_is_installed(self, host):
        assert host.package("lvm2").is_installed

    def test_chrony_package_is_installed(self, host):
        assert host.package("chrony").is_installed

    def test_podman_package_is_installed(self, host):
        assert host.package("podman").is_installed

    def test_chronyd_is_active(self, host):
        svc = host.service("chronyd")
        assert svc.is_enabled
        assert svc.is_running
