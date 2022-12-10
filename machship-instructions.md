1. Locally, Prepare target hosts
2. On ceph-deploy, the ansible playbook _cephadm-setup.yml -l '!ceph-deploy': 
3. - import_playbook: cephadm-preflight.yml
- import_playbook: cephadm-bootstrap.yml
- import_playbook: cephadm-osd.yml
- import_playbook: cephadm-create-cephfs.yml
- import_playbook: cephadm-nfs.yml

