.. contents::

Introduction
------------

cephadm-ansible is a collection of Ansible modules and playbooks to simplify
workflows that are not covered by [cephadm]_. They are covered by the following playbooks:

* cephadm-preflight.yml: Initial setup of hosts before bootstrapping the cluster
* cephadm-clients.yml: Setting up client hosts
* cephadm-purge-cluster.yml: Remove a Ceph cluster
* cephadm-distribute-ssh-key.yml: Distribute a SSH public key to all hosts
* cephadm-set-container-insecure-registries.yml: Add a block in /etc/containers/registries.conf to add an insecure registry

Additionnally, several ansible modules are provided in order to let people writing their own playbooks.


.. [cephadm] https://docs.ceph.com/en/latest/cephadm/

Terminology
-----------

**admin host**
  A host where the admin keyring and ceph config file are present. Although the admin host and the bootstrap host are usually the same host, it is possible to have multiple admin hosts later.
  ``cephadm`` will make a host become 'admin' when the label ``_admin`` is added to that host. (ie: ``ceph orch host label add <host> _admin``).
  This hosts should be present in the group ``[admin]`` in the ansible inventory.
  If for some reason you decide a host shouldn't be a 'admin host' anymore, you have to :

  * remove it from the group ``[admin]`` in the ansible inventory,
  * remove the admin keyring,
  * remove the ceph config file,
  * remove the ``_admin`` label. (ie ``ceph orch host label rm <host> _admin``)


**ansible host**
  The host where any cephadm-ansible playbook is run.

**bootstrap host**
  The host where the ceph cluster will start. Unless you pass the ``--skip-admin-label`` option to the ``ceph bootstram`` command, this host will receive the admin keyring and the ceph config file and should be considered as an 'admin host'.
  This host should be present in the group ``[admin]`` in the ansible inventory.


Ansible inventory
-----------------
The ansible inventory is a file where all the hosts intended to be part of the ceph cluster will be listed.
The most common format are INI or YAML.

Although you probably want to keep it as simple as possible, you can organize your inventory and create groups, `cephadm-ansible` won't differentiate except for the following requirements:

* Client hosts must be defined in a dedicated group ``[clients]``.
* Both ``cephadm-purge-cluster.yml`` and ``cephadm-clients.yml`` playbooks require a group ``[admin]`` with at least one admin host (usually it will be the bootstrap node).

.. note:: the name of the client group can be changed. In that case you have to set the variable `client_group`.

Otherwise, you can create groups such as ``[monitors]``, ``[osds]``, ``[rgws]``, that might help you keep clarity in your inventory file and ease the ``--limit`` usage if you plan to use it to target specific a group of hosts only.

A basic inventory would look like following::

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


Playbooks
---------

cephadm-preflight
=================

This playbook configures the Ceph repository.
It also installs some prerequisites (podman, lvm2, chronyd, cephadm, ...)

Usage::

   ansible-playbook -i <inventory host file> cephadm-preflight.yml


You can limit the execution to a set of hosts by using ``--limit`` option::

   ansible-playbook -i <inventory host file> cephadm-preflight.yml --limit <my_osd_group|my_node_name>


You can override variables using ``--extra-vars`` parameter::


   ansible-playbook -i <inventory host file> cephadm-preflight.yml --extra-vars "ceph_origin=rhcs"



Options
+++++++

ceph_origin
~~~~~~~~~~~
**description**
  The source of Ceph repositories.


**valid values**

``rhcs``
  Repository from Red Hat Ceph Storage.
``community``
  Community repository (https://download.ceph.com)
``custom``
  Custom repository.
  When ``ceph_origin: custom`` is defined, you have to set the variable ``custom_repo_url`` with the URL of your repository.
  Passing the extra-var ``-e custom_repo_state=absent`` allows you to remove this repository later.

  It also supports deploying multiple repositories, in that case you must set the variable ``ceph_custom_repositories`` instead.
  ``ceph_custom_repositories`` is a dictionnary that should look like following::

    ceph_custom_repositories:
      - name: ceph_custom_noarch
        state: present
        description: Ceph custom repo noarch
        gpgcheck: 'no'
        baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/noarch
        file: ceph_shaman_build_noarch
        priority: '2'
        enabled: 1
      - name: ceph_custom_x86_64
        state: present
        description: Ceph custom repo x86_64
        gpgcheck: 'no'
        baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/x86_64
        file: ceph_shaman_build_x86_64
        priority: '2'
        enabled: 1

  Given that the definition is more complex, you might want to define it as a group_vars/host_vars rather than as an extra-var::

    $ cat group_vars/all
    ---
    ceph_custom_repositories:
      - name: ceph_custom_noarch
        state: present
        description: Ceph custom repo noarch
        gpgcheck: 'no'
        baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/noarch
        file: ceph_shaman_build_noarch
        priority: '2'
        enabled: 1
      - name: ceph_custom_x86_64
        state: present
        description: Ceph custom repo x86_64
        gpgcheck: 'no'
        baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/x86_64
        file: ceph_shaman_build_x86_64
        priority: '2'
        enabled: 1


``shaman``
  Devel repository.

**default**
  "community"

ceph_stable_key
~~~~~~~~~~~~~~~~
**description**
  URL to the gpg key.

**default**
  https://download.ceph.com/keys/release.asc

ceph_release
~~~~~~~~~~~~
**description**
  The release of Ceph.

**default**
  Corresponding Ceph release.

ceph_dev_branch
~~~~~~~~~~~~~~~
**description**
  The development branch to be used in shaman when `ceph_origin` is 'shaman'.

**default**
  "main"

ceph_dev_sha1
~~~~~~~~~~~~~
**description**
  The sha1 corresponding to the build to be used when `ceph_origin` is 'shaman'.

**default**
  "latest"

custom_repo_url
~~~~~~~~~~~~~~~
**description**
  The url of the repository when ``ceph_origin`` is 'custom'.
  Mutually exclusive with ``ceph_custom_repositories``.

ceph_custom_repositories
~~~~~~~~~~~~~~~~~~~~~~~~

This variable is a list.
Mutually exclusive with ``custom_repo_url``.
The following options can be specified for each element that represents a repository to be set up:

name
####
**description**
  The name of the repository.

gpgkey
######
**description**
  The url of the gpg key corresponding to the repository being set up.

gpgcheck
########
**description**
  Whether gpgcheck has to be performed.

state
#####
**description**
  Whether this repository has to be present or absent. (Default: present)

description
###########
**description**
  A short repository description

baseurl
#######
**description**
  The url of the repository pointing to the location where 'repodata' directory lives.

file
####
**description**
  The filename Ansible will use to write the repository file.

priority
########
**description**
  The priority of this repository.

components
##########
**description**
  This is a Debian OS-based family parameter only.
  The components of this ubuntu/debian repository.


Example::

  ceph_custom_repositories:
    - name: ceph_custom_noarch
      state: present
      description: Ceph custom repo noarch
      gpgcheck: 'no'
      baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/noarch
      file: ceph_shaman_build_noarch
      priority: '2'
    - name: ceph_custom_x86_64
      state: present
      description: Ceph custom repo x86_64
      gpgcheck: 'no'
      baseurl: https://4.chacra.ceph.com/r/ceph/main/cf17ed16c3964b635e9b6c22e607ea5672341c5c/centos/8/flavors/default/x86_64
      file: ceph_shaman_build_x86_64
      priority: '2'

set_insecure_registries
~~~~~~~~~~~~~~~~~~~~~~~
**description**
  Whether ``cephadm-preflight.yml`` playbook will call ``cephadm-set-container-insecure-registries.yml`` to add an insecure registry in ``/etc/containers/registries.conf``.
  ``insecure_registry`` option must be passed (-e insecure_registry=<registry url>)

**default**
  false

cephadm-set-container-insecure-registries
=========================================

This playbook adds a block in ``/etc/containers/registries.conf`` in order to allow an insecure registry to be used.

Usage::

   ansible-playbook -i <inventory host file> cephadm-set-container-insecure-registries.yml -e insecure_registry=<registry url>



Options
+++++++

insecure_registry
~~~~~~~~~~~~~~~~~
**description**
  The address of the insecure registry to be added to ``/etc/containers/registries.conf``.

**default**
  No default.

cephadm-distribute-ssh-key
==========================

This playbook distributes an SSH public key over all hosts present in the inventory.
The key to be copied will be read from a file specified at the path defined in ``cephadm_pubkey_path`` **from the Ansible controller host**.
If ``cephadm_pubkey_path`` is unset, the playbook will assume it is supposed to get it from the command ``cephadm get-pub-key``.

Usage::

  ansible-playbook -i <inventory host file> cephadm-distribute-ssh-key.yml -e admin_node=ceph-node01 -e cephadm_pubkey_path=/home/cephadm/ceph.key

Options
+++++++

fsid
~~~~
**description**
  The fsid of the Ceph cluster.

admin_node
~~~~~~~~~~
**description**
  The name of a node with enough privileges to call `cephadm get-pub-key` command.
  (usually the bootstrap node).

cephadm_ssh_user
~~~~~~~~~~~~~~~~
**description**
  The ssh username on remote hosts that will be used by ``cephadm``.

cephadm_pubkey_path
~~~~~~~~~~~~~~~~~~~
**description**
  Full path name of the ssh public key file **on the ansible controller host**.



cephadm-purge
=============

This playbook purges a Ceph cluster managed with cephadm

You must define a group ``[admin]`` in your inventory with a node where
the admin keyring is present at ``/etc/ceph/ceph.client.admin.keyring``

Usage::

   ansible-playbook -i <inventory host file> cephadm-purge-cluster.yml -e fsid=<your fsid>

Options
+++++++

fsid
~~~~
**description**
  The fsid of the cluster.


cephadm-clients
===============

If you plan to deploy client nodes, you must define a group called "clients" in your inventory::

   $ cat hosts
   node1
   node2
   node3

   [clients]
   client1
   client2
   client3
   node123

This playbooks distribute keyring and conf files to a set of client hosts.

Usage::

   ansible-playbook -i <inventory host file> cephadm-clients.yml -e fsid=<cluster fsid> -e keyring=<path to the keyring>

Options
+++++++

keyring
~~~~~~~~
**description**
  The full path name of the keyring file on the host (which should be admin[0]) which holds the key for the client to use

conf
~~~~
**description**
  The full path name of the conf file on the (which should be admin[0]) host to use (undefined will trigger a minimal conf)

keyring_dest
~~~~~~~~~~~~
**description**
  The full path name of the destination where the keyring will be copied on the remote host. (default: /etc/ceph/ceph.keyring)


rocksdb-resharding
==================

This playbook reshards the rocksDB database for a given OSD.

Usage::

  ansible-playbook -i <inventory host file> rocksdb-resharding.yml -e osd_id=0 -e admin_node=ceph-mon0 -e rocksdb_sharding_parameters='m(3) p(3,0-12) O(3,0-13) L P'

Options
+++++++

fsid
~~~~
**description**
  The fsid of the Ceph cluster.

osd_id
~~~~~~
**description**
  The id of the OSD where you want to reshard its corresponding rocksdb database.

admin_node
~~~~~~~~~~
**description**
  The name of a node with enough privileges to stop/start daemons via `cephadm shell ceph orch daemon` command.
  (Usually the bootstrap node)

rocksdb_sharding_parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~
**description**
  The rocksdb sharding parameter to set. Default is 'm(3) p(3,0-12) O(3,0-13) L P'.

docker
~~~~~~
  A boolean to be set in order to tell the playbook cephadm uses ``docker`` instead of ``podman`` as container engine. Default is ``False``.


Modules
-------

Introduction
============

cephadm-ansible provides several modules to make it easier to write playbooks around cephadm/ceph orch.
The idea is to let you write your own playbooks, rather than providing a unique playbook that would try to cover anyone's use case.
This way you can have a solution that fits better with your needs.

At the moment only the most important tasks are supported.
This means that any operation not covered would have to be done either with either the ``command`` or ``shell`` Ansible tasks in your playbook.

Module descriptions
===================

cephadm_bootstrap
+++++++++++++++++

``mon_ip``
  Ceph monitor IP address.
``image``
  Ceph container image.
``docker``
  Use docker instead of podman.
``fsid``
  Ceph FSID.
``pull``
  Pull the Ceph container image.
``dashboard``
  Deploy the Ceph dashboard.
``dashboard_user``
  Ceph dashboard user.
``dashboard_password``
  Ceph dashboard password.
``monitoring``
  Deploy the monitoring stack.
``firewalld``
  Manage firewall rules with firewalld.
``allow_overwrite``
  allow overwrite of existing -output-* config/keyring/ssh files.
``registry_url``
  URL for custom registry.
``registry_username``
  Username for custom registry.
``registry_password``
  Password for custom registry.
``registry_json``
  JSON file with custom registry login info (URL, username, password).
``ssh_user``
  SSH user used for cephadm ssh to the hosts.
``ssh_config``
  SSH config file path for cephadm ssh client.
``allow_fqdn_hostname``
  Allow hostname that is fully-qualified.
``cluster_network``
  Subnet to use for cluster replication, recovery and heartbeats.


ceph_orch_host
++++++++++++++

``fsid``
  The fsid of the Ceph cluster to interact with.
``image``
  Ceph container image.
``name``
  name of the host to be added/removed/updated.
``address``
  address of the host, required when ``state`` is ``present``.
``set_admin_label``
  enforce '_admin' label on the host specified in 'name'.
``labels``
  list of labels to apply on the host.
``state``
  If set to 'present', it will ensure the host specified in 'name' will be present along with the labels specified in ``labels``.
  If set to 'absent', it will remove the host specified in 'name'.
  If set to 'drain', it will schedule to remove all daemons from the host specified in 'name'.


ceph_config
+++++++++++

``fsid``
  The fsid of the Ceph cluster to interact with.
``image``
  Ceph container image.
``action``
  Whether to get or set the parameter specified in 'option'.
``who``
  Which daemon the configuration should be set to.
``option``
  Name of the parameter to be set.
``value``
  Value of the parameter to set.

ceph_orch_apply
+++++++++++++++

``fsid``
  The fsid of the Ceph cluster to interact with.
``image``
  Ceph container image.
``spec``
  The service spec to apply.


ceph_orch_daemon
++++++++++++++++

``fsid``
  The fsid of the Ceph cluster to interact with.
``image``
  Ceph container image.
``state``
  The desired state of the service specified in 'name'.
  If 'started', it ensures the service is started.
  If 'stopped', it ensures the service is stopped.
  If 'restarted', it will restart the service.
``daemon_id``
  The id of the service.
``daemon_type``
  The type of the service.

cephadm_registry_login
++++++++++++++++++++++

``state``
  Whether the module should log in to the registry or log out.
``registry_url``
  The container registry to log in or log out.
``registry_username``
  The username to log in to the container registry.
``registry_password``
  The corresponding password to be used with ``registry_username``.

Samples
=======

This shows how the supported modules can be used in a playbook.
This doesn't cover the pre-requisites steps (preflight, ...) so it implies all requirements are satisfied (podman, lvm2,...).
It assumes your "bootstrap host" (or "admin host") can ssh to other hosts with root user without password.

Bootstrap and add some hosts::

   # cat hosts
   ceph-mon1 monitor_address=10.10.10.101 labels="['_admin', 'mon', 'mgr']"
   ceph-mon2 labels="['mon', 'mgr']"
   ceph-mon3 labels="['mon', 'mgr']"
   ceph-osd1 labels="['osd']"
   ceph-osd2 labels="['osd']"
   ceph-osd3 labels="['osd']"
   # cat site.yml
   ---
   - name: bootstrap the cluster
     hosts: ceph-mon1
     become: true
     gather_facts: false
     tasks:
       - name: login to quay.io registry
         cephadm_registry_login:
           state: login
           registry_url: quay.io
           registry_username: foo
           registry_password: b4r

       - name: bootstrap initial cluster
         cephadm_bootstrap:
           mon_ip: "{{ monitor_address }}"

   - name: add more hosts
     hosts: all
     become: true
     gather_facts: true
     tasks:
       - name: add hosts to the cluster
         ceph_orch_host:
           name: "{{ ansible_facts['hostname'] }}"
           address: "{{ ansible_facts['default_ipv4']['address'] }}"
           labels: "{{ labels }}"
         delegate_to: ceph-mon1

   - name: deploy osd service
     hosts: ceph-mon1
     become: true
     gather_facts: false
     tasks:
       - name: apply osd spec
         ceph_orch_apply:
         spec: |
           service_type: osd
           service_id: osd
           placement:
             host_pattern: '*'
             label: osd
           spec:
             data_devices:
               all: true

   - name: change osd_default_notify_timeout option
     hosts: ceph-mon1
     become: true
     gather_facts: false
     tasks:
       - name: decrease the value of osd_default_notify_timeout option
         ceph_config:
           action: set
           who: osd
           option: osd_default_notify_timeout
           value: 20


.. note:: You may have noticed that most of the time, the target node in the different plays in the playbook above is ``ceph-mon1``, which is the bootstrap node.

Upcoming changes
----------------

.. important:: The name of the project might change in the next release.

.. important:: In the next release, this project will be distributed as an Ansible collection.
