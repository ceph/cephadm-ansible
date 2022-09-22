import pytest
import json


class TestCluster(object):
    @pytest.mark.admin
    def test_hosts_have_expected_labels(self, node, host):
        inventory_variables = host.ansible('debug', 'msg="{{ hostvars }}"')['msg']
        result = host.run('cephadm shell ceph orch host ls --format json')
        self.host_ls = json.loads(result.stdout)

        for h in self.host_ls:
            name = h['hostname']
            assert sorted(inventory_variables[name]['labels']) == sorted(h['labels'])
