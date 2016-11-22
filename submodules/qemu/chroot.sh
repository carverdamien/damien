#!/bin/bash
set -e -x
sudo cp -a debootstrap chroot
sudo chroot chroot < chroot_cmd.sh
