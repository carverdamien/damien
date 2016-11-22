#!/bin/bash
set -e -x
IMAGE=image
: ${SIZE:=1073741824}
! (mount | grep ${IMAGE}.tmp)
dd if=/dev/zero of=${IMAGE}.tmp bs=1M count=$((SIZE / 2**20))
mkfs.ext4 -F ${IMAGE}.tmp
tune2fs -O ^has_journal ${IMAGE}.tmp
mkdir .mnt
sudo mount ${IMAGE}.tmp .mnt
sudo cp -a chroot/. .mnt/.
sudo umount .mnt
rmdir .mnt
mv ${IMAGE}.tmp ${IMAGE}
e2fsck -f -y ${IMAGE}
