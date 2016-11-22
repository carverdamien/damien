#!/bin/bash
set -e -x
suite=wheezy
mirror=http://http.debian.net/debian/
packages=ca-certificates,apt-transport-https,cgroup-bin,sysstat,openssh-server
sudo debootstrap --include=${packages} ${suite} debootstrap ${mirror}
