import pytest

@pytest.fixture()
def node(host, request):
    ansible_vars = host.ansible.get_variables()

    if request.node.get_closest_marker("no_client") and ansible_vars['group_names'] == ['clients']:
        pytest.skip("Not a valid test for client nodes")

