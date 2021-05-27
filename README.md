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

## Enabling the `ceph` CLI

It is recommended to also install the ceph-common package in order to access the 
`ceph` binary.

```
ansible-playbook -i hosts -v cephadm-preflight.yml -e "ceph_pkgs=ceph-common"
```

# Purge

This playbook purges a Ceph cluster managed with cephadm

You must define a group `[admin]` in your inventory with a node where
the admin keyring is present at `/etc/ceph/ceph.client.admin.keyring`

## Usage:

```
ansible-playbook -i <inventory host file> cephadm-purge-cluster.yml -e fsid=<your fsid>
```

[cephadm]: https://docs.ceph.com/en/latest/cephadm/
