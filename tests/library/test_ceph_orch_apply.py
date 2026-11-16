from mock.mock import MagicMock
import ceph_orch_apply

OSD_SPECS = """\
service_type: osd
service_id: all-available-devices
service_name: osd.all-available-devices
placement:
  label: osds
spec:
  data_devices:
    all: true
---
service_type: osd
service_id: fast
service_name: osd.fast
placement:
  label: fast
spec:
  data_devices:
    rotational: 0
"""


def _module(stdout, rc=0):
    module = MagicMock()
    module.params = {'fsid': None, 'image': None, 'docker': False}
    module.run_command.return_value = (rc, stdout, '')
    return module


class TestRetrieveCurrentSpec(object):

    def test_multiple_documents_pick_matching_service_id(self):
        expected = {'service_type': 'osd', 'service_id': 'fast'}
        current = ceph_orch_apply.retrieve_current_spec(_module(OSD_SPECS), expected)
        assert current['service_id'] == 'fast'
        assert current['placement'] == {'label': 'fast'}

    def test_multiple_documents_no_match_means_change_required(self):
        expected = {'service_type': 'osd', 'service_id': 'other',
                    'placement': {'label': 'other'}}
        current = ceph_orch_apply.retrieve_current_spec(_module(OSD_SPECS), expected)
        assert ceph_orch_apply.change_required(current, expected)

    def test_single_document_without_service_id(self):
        stdout = "service_type: ceph-exporter\nservice_name: ceph-exporter\nplacement:\n  count_per_host: 1\n"
        expected = {'service_type': 'ceph-exporter', 'placement': {'count_per_host': 1}}
        current = ceph_orch_apply.retrieve_current_spec(_module(stdout), expected)
        assert not ceph_orch_apply.change_required(current, expected)

    def test_no_services_reported(self):
        expected = {'service_type': 'osd', 'service_id': 'fast'}
        current = ceph_orch_apply.retrieve_current_spec(_module('No services reported\n'), expected)
        assert current == {}
        assert ceph_orch_apply.change_required(current, expected)
