# cephadm-ansible

cephadm-ansible is a collection of Ansible playbooks to simplify
workflows that are not covered by [cephadm]. The workflows covered
are:

* Preflight: Initial setup of hosts before bootstrapping the cluster
* Client: Setting up client hosts
* Purge: Remove a Ceph cluster


# Terminology
**<ins>admin host</ins>:**\
A host where the admin keyring and ceph config file is present.\
Although the admin host and the bootstrap host are usually the same host, it is possible to have multiple admin hosts later.\
`cephadm` will make a host become 'admin' when the label `_admin` is added to that host. (ie: `ceph orch host label add <host> _admin`).\
This hosts should be present in the group `[admin]` in the ansible inventory.\
If for some reason you decide a host shouldn't be a 'admin host' anymore, you have to :

* remove it from the group `[admin]` in the ansible inventory,
* remove the admin keyring,
* remove the ceph config file,
* remove the '_admin' label. (ie `ceph orch host label rm <host> _admin`)


**<ins>ansible host</ins>:**\
The host where any cephadm-ansible playbook is run.

**<ins>bootstrap host</ins>:**\
The host where the ceph cluster will start.\
Unless you pass `--skip-admin-label` option to `ceph bootstram` command, this host will get the admin keyring and the ceph config file present, therefore, it should be considered as an 'admin host'.
This hosts should be present in the group `[admin]` in the ansible inventory.


# Ansible inventory
The ansible inventory is a file where all the hosts intended to be part of the ceph cluster will be listed.\
The most common format are INI or YAML.

Although you probably want to keep it as simple as possible, you can organize your inventory and create groups, `cephadm-ansible` won't make any difference except for the following requirements:

* Client hosts must be defined in a dedicated group `[clients]`.
* Both `cephadm-purge-cluster.yml` and `cephadm-clients.yml` playbooks requires a group `[admin]` with at least one admin host (usually it will be the bootstrap node).

> **__NOTE:__** the name of the client group can be changed. In that case you have to set the variable `client_group`.

Otherwise, you can create groups such as `[monitors]`, `[osds]`, `[rgws]`, that might help you keep clarity in your inventory file and probably ease the `--limit` usage if you plan to use it to target a group of node only.

A basic inventory would look like following:

```ini
# cat hosts
ceph-mon1
ceph-mon2
ceph-mon3
ceph-osd1
ceph-osd2
ceph-osd3
ceph-mds1
ceph-mds2
ceph-rgw1
ceph-rgw2

[clients]
ceph-client1
ceph-client2
ceph-client3

[admin]
ceph-mon1
```


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

If you plan to deploy client nodes, you must define a group called "clients" in your inventory:

eg:

```
$ cat hosts
node1
node2
node3

[clients]
client1
client2
client3
node123
```

Then you can run the playbook as shown above.

Options:

`ceph_origin`: The source of Ceph repositories.\
**valid values:**

* `rhcs`: Repository from Red Hat Ceph Storage.
* `community`: Community repository (https://download.ceph.com)
* `custom`: Custom repository.
* `shaman`: Devel repository.

**default**: community

`ceph_stable_key`: URL to the gpg key.\
**default**: https://download.ceph.com/keys/release.asc

`ceph_release`: The release of Ceph.
**default**: pacific

`ceph_dev_branch`: The development branch to be used in shaman when `ceph_origin` is 'shaman'.\
**default**: master

`ceph_dev_sha1`: The sha1 corresponding to the build to be used when `ceph_origin` is 'shaman'.\
**default**: latest

`custom_repo_url`: The url of the repository when `ceph_origin` is 'custom'.
`custom_repo_gpgkey`: The url of the gpg key corresponding to the repository set in `custom_repo_url` when `ceph_origin` is 'custom'.

# Purge

This playbook purges a Ceph cluster managed with cephadm

You must define a group `[admin]` in your inventory with a node where
the admin keyring is present at `/etc/ceph/ceph.client.admin.keyring`

## Usage:

```
ansible-playbook -i <inventory host file> cephadm-purge-cluster.yml -e fsid=<your fsid>
```

[cephadm]: https://docs.ceph.com/en/latest/cephadm/
