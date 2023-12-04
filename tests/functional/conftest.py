import pytest

@pytest.fixture()
def node(host, request):
    ansible_vars = host.ansible.get_variables()

    if request.node.get_closest_marker("no_client") and 'clients' in ansible_vars['group_names']:
        pytest.skip("Not a valid test for client nodes")

    if request.node.get_closest_marker("client") and 'clients' not in ansible_vars['group_names']:
        pytest.skip("Not a valid test for non client nodes")

    if request.node.get_closest_marker("osd") and 'osds' not in ansible_vars['group_names']:
        pytest.skip("Not a valid test for non osd nodes")

    if request.node.get_closest_marker("admin") and 'admin' not in ansible_vars['group_names']:
        pytest.skip("Not a valid test for non admin nodes")

    return ansible_vars
