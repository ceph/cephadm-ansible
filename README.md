# cephadm-ansible

cephadm-ansible is a collection of Ansible playbooks to simplify
workflows that are not covered by [cephadm]. The workflows covered
are:

* Preflight: Initial setup of hosts before bootstrapping the cluster
* Client: Setting up client hosts
* Purge: Remove a Ceph cluster

# Preflight

This playbook configures the Ceph repository.
It also installs some prerequisites (podman, lvm2, chronyd, cephadm, ...)

## Usage:

```
ansible-playbook -i <inventory host file> cephadm-preflight.yml
```

You can limit the execution to a set of hosts by using `--limit` option:

```
ansible-playbook -i <inventory host file> cephadm-preflight.yml --limit <my_osd_group|my_node_name>
```

You can override variables using `--extra-vars` parameter:

```
ansible-playbook -i <inventory host file> cephadm-preflight.yml --extra-vars "ceph_origin=rhcs"
```

[cephadm]: https://docs.ceph.com/en/latest/cephadm/
