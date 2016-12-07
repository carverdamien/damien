#!/bin/bash
: ${KERNEL:=/home/dc/Git/linux/build/acdc/arch/x86/boot/bzImage}
sudo qemu-system-x86_64 \
-cpu host -smp cores=4,threads=2,sockets=1 \
-m 4G \
-enable-kvm \
-kernel "${KERNEL}" \
-chardev stdio,id=stdio,mux=on,signal=off \
-device virtio-serial-pci \
-device virtconsole,chardev=stdio \
-mon chardev=stdio \
-display none \
-net user \
-net nic,model=virtio \
-redir tcp:80::80 \
-redir tcp:2222::22 \
-drive file=image,if=virtio,cache=none \
-append 'root=/dev/vda console=hvc0'
