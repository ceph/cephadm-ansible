import pytest

class TestPurge(object):
    @pytest.mark.osd
    @pytest.mark.parametrize("device", ['/dev/sda', '/dev/sdb', '/dev/sdc'])
    def test_devices_are_available(self, host, device):
        assert host.run('python3 -c "import os; fd = os.open({}, (os.O_RDWR | os.O_EXCL), 0); os.close(fd)"'.format(device))
