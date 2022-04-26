#!/bin/bash

vagrant box remove centos/stream8 --all --force || true
vagrant box add --name centos/stream8 https://cloud.centos.org/centos/8-stream/x86_64/images/CentOS-Stream-Vagrant-8-20220125.1.x86_64.vagrant-libvirt.box --force

retries=0
until [ $retries -ge 5 ]
do
  echo "Attempting to start VMs. Attempts: $retries"
  timeout 10m time vagrant up "$@" && break
  retries=$[$retries+1]
  sleep 5
done

sleep 10
